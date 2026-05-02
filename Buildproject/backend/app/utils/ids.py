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


def generate_agent_run_id(agent_type: str) -> str:
    """
    Generate agent run ID in format: run_{agent_type}_{timestamp}
    Example: run_verification_1714567890123
    
    Args:
        agent_type: Type of agent (e.g., 'verification', 'dispatch')
    
    Returns:
        Formatted agent run ID string
    """
    timestamp = int(time.time() * 1000)
    return f"run_{agent_type}_{timestamp}"


def generate_alert_id(crisis_type: str, sequence: Optional[int] = None) -> str:
    """
    Generate alert ID in format: alert_{type}_{sequence}
    Example: alert_fire_001
    
    Args:
        crisis_type: Type of crisis (e.g., 'fire', 'flood')
        sequence: Optional sequence number, if None generates timestamp-based
    
    Returns:
        Formatted alert ID string
    """
    if sequence is None:
        sequence = int(time.time() * 1000) % 100000
    return f"alert_{crisis_type.lower()}_{sequence:05d}"


def generate_dispatch_id(crisis_type: str, sequence: Optional[int] = None) -> str:
    """
    Generate dispatch ID in format: dispatch_{type}_{sequence}
    Example: dispatch_fire_001
    
    Args:
        crisis_type: Type of crisis (e.g., 'fire', 'flood')
        sequence: Optional sequence number, if None generates timestamp-based
    
    Returns:
        Formatted dispatch ID string
    """
    if sequence is None:
        sequence = int(time.time() * 1000) % 100000
    return f"dispatch_{crisis_type.lower()}_{sequence:05d}"

# Made with Bob
