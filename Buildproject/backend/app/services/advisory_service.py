"""
Advisory service for generating safety recommendations.
Provides crisis-specific safety playbooks and AI-enhanced advice.
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
import logging
from datetime import datetime

from app.models.incident import Incident
from app.schemas.common import CrisisType, AgentName, AgentRunStatus
from app.schemas.advisory import SafetyAction, AdvisoryResponse
from app.services.watsonx_service import watsonx_service
from app.services.cloudant_service import cloudant_service
from app.utils.geo import haversine_distance
from app.utils.ids import generate_agent_run_id
from app.utils.time import utc_now

logger = logging.getLogger(__name__)


class AdvisoryService:
    """Service for generating safety advisories based on incident types."""
    
    # Safety playbooks for each crisis type
    SAFETY_PLAYBOOKS = {
        CrisisType.FIRE: {
            "playbook_id": "FIRE_STANDARD",
            "immediate_actions": [
                {
                    "priority": 1,
                    "action": "Evacuate immediately if fire is nearby",
                    "rationale": "Fire spreads rapidly and smoke inhalation is the leading cause of fire deaths"
                },
                {
                    "priority": 2,
                    "action": "Stay low to the ground to avoid smoke",
                    "rationale": "Smoke rises and cleaner air is found near the floor"
                },
                {
                    "priority": 3,
                    "action": "Alert others and call emergency services",
                    "rationale": "Early warning saves lives and ensures rapid response"
                }
            ],
            "what_to_do": [
                "Alert others in the building immediately",
                "Use stairs, never elevators during a fire",
                "Close doors behind you to slow fire spread",
                "Feel doors before opening - if hot, find another route",
                "If clothes catch fire: Stop, Drop, and Roll",
                "Once outside, stay out and call 999"
            ],
            "what_not_to_do": [
                "Do not stop to collect belongings",
                "Do not use elevators",
                "Do not re-enter the building for any reason",
                "Do not open doors that are hot to touch",
                "Do not hide - evacuate immediately"
            ],
            "evacuation_template": "Move at least {radius} meters away from the fire. Head upwind if possible to avoid smoke.",
            "emergency_contacts": [
                {"service": "Fire Service", "number": "999"},
                {"service": "Emergency Hotline", "number": "112"}
            ]
        },
        CrisisType.FLOOD: {
            "playbook_id": "FLOOD_STANDARD",
            "immediate_actions": [
                {
                    "priority": 1,
                    "action": "Move to higher ground immediately",
                    "rationale": "Floodwaters can rise rapidly and become life-threatening"
                },
                {
                    "priority": 2,
                    "action": "Avoid walking or driving through floodwater",
                    "rationale": "Just 6 inches of moving water can knock you down; 2 feet can sweep away vehicles"
                },
                {
                    "priority": 3,
                    "action": "Turn off utilities if instructed",
                    "rationale": "Prevents electrical hazards and gas leaks"
                }
            ],
            "what_to_do": [
                "Move to the highest floor or roof if trapped",
                "Take emergency supplies and important documents",
                "Listen to emergency broadcasts for updates",
                "Signal for help if trapped",
                "Avoid contact with floodwater (may be contaminated)",
                "Document damage with photos for insurance"
            ],
            "what_not_to_do": [
                "Do not walk through moving water",
                "Do not drive through flooded areas",
                "Do not touch electrical equipment if wet",
                "Do not drink floodwater",
                "Do not return home until authorities say it's safe"
            ],
            "evacuation_template": "Evacuate to higher ground at least {radius} meters from the flood zone. Follow designated evacuation routes.",
            "emergency_contacts": [
                {"service": "Disaster Management", "number": "999"},
                {"service": "Emergency Hotline", "number": "112"}
            ]
        },
        CrisisType.WILDLIFE: {
            "playbook_id": "WILDLIFE_STANDARD",
            "immediate_actions": [
                {
                    "priority": 1,
                    "action": "Keep a safe distance from the animal",
                    "rationale": "Wild animals are unpredictable and may attack if they feel threatened"
                },
                {
                    "priority": 2,
                    "action": "Do not run - back away slowly",
                    "rationale": "Running triggers chase instinct in many predators"
                },
                {
                    "priority": 3,
                    "action": "Make yourself appear larger if confronted",
                    "rationale": "Many animals will avoid confrontation with larger threats"
                }
            ],
            "what_to_do": [
                "Stay calm and assess the situation",
                "Keep children and pets close",
                "Make noise to alert the animal of your presence",
                "Back away slowly while facing the animal",
                "Seek shelter indoors if possible",
                "Report sighting to wildlife authorities"
            ],
            "what_not_to_do": [
                "Do not approach or feed the animal",
                "Do not run or make sudden movements",
                "Do not corner the animal",
                "Do not play dead unless it's a specific species (e.g., grizzly bear)",
                "Do not leave small children or pets unattended"
            ],
            "evacuation_template": "Maintain at least {radius} meters distance. Move indoors and secure all entry points.",
            "emergency_contacts": [
                {"service": "Wildlife Authority", "number": "999"},
                {"service": "Emergency Hotline", "number": "112"}
            ]
        },
        CrisisType.ACCIDENT: {
            "playbook_id": "ACCIDENT_STANDARD",
            "immediate_actions": [
                {
                    "priority": 1,
                    "action": "Ensure your own safety first",
                    "rationale": "You cannot help others if you become a victim"
                },
                {
                    "priority": 2,
                    "action": "Call emergency services immediately",
                    "rationale": "Professional medical help is critical for serious injuries"
                },
                {
                    "priority": 3,
                    "action": "Provide first aid if trained and safe to do so",
                    "rationale": "Immediate first aid can save lives while waiting for help"
                }
            ],
            "what_to_do": [
                "Turn on hazard lights if in a vehicle",
                "Move to a safe location away from traffic",
                "Check for injuries but don't move seriously injured people",
                "Control bleeding with direct pressure if trained",
                "Keep injured people warm and calm",
                "Document the scene with photos if safe"
            ],
            "what_not_to_do": [
                "Do not move seriously injured people unless in immediate danger",
                "Do not remove helmets from motorcyclists",
                "Do not give food or water to seriously injured people",
                "Do not leave the scene before authorities arrive",
                "Do not admit fault or make statements about liability"
            ],
            "evacuation_template": "Move at least {radius} meters from the accident site to avoid secondary incidents.",
            "emergency_contacts": [
                {"service": "Ambulance", "number": "999"},
                {"service": "Police", "number": "999"},
                {"service": "Emergency Hotline", "number": "112"}
            ]
        },
        CrisisType.SECURITY: {
            "playbook_id": "SECURITY_STANDARD",
            "immediate_actions": [
                {
                    "priority": 1,
                    "action": "Move to a safe location immediately",
                    "rationale": "Your safety is the top priority in any security threat"
                },
                {
                    "priority": 2,
                    "action": "Call police and report the threat",
                    "rationale": "Law enforcement needs immediate notification to respond effectively"
                },
                {
                    "priority": 3,
                    "action": "Alert others in the area if safe to do so",
                    "rationale": "Warning others can prevent additional victims"
                }
            ],
            "what_to_do": [
                "Lock doors and windows if sheltering in place",
                "Turn off lights and stay quiet",
                "Stay away from windows and doors",
                "Follow instructions from authorities",
                "Keep your phone charged and accessible",
                "Have an escape route planned"
            ],
            "what_not_to_do": [
                "Do not confront the threat",
                "Do not post real-time updates on social media",
                "Do not ignore official warnings",
                "Do not use elevators during evacuation",
                "Do not return to the area until cleared by police"
            ],
            "evacuation_template": "Evacuate to a safe location at least {radius} meters away. Follow police instructions.",
            "emergency_contacts": [
                {"service": "Police", "number": "999"},
                {"service": "Emergency Hotline", "number": "112"}
            ]
        },
        CrisisType.HEALTH: {
            "playbook_id": "HEALTH_STANDARD",
            "immediate_actions": [
                {
                    "priority": 1,
                    "action": "Avoid the affected area",
                    "rationale": "Prevents exposure to potential health hazards"
                },
                {
                    "priority": 2,
                    "action": "Seek medical attention if experiencing symptoms",
                    "rationale": "Early medical intervention improves outcomes"
                },
                {
                    "priority": 3,
                    "action": "Follow public health guidance",
                    "rationale": "Health authorities provide evidence-based recommendations"
                }
            ],
            "what_to_do": [
                "Wash hands frequently with soap and water",
                "Wear protective equipment if recommended",
                "Monitor yourself for symptoms",
                "Follow quarantine or isolation instructions",
                "Keep emergency contacts informed",
                "Stock up on necessary medications"
            ],
            "what_not_to_do": [
                "Do not ignore symptoms",
                "Do not self-medicate without medical advice",
                "Do not spread unverified health information",
                "Do not visit healthcare facilities without calling first",
                "Do not panic - follow official guidance"
            ],
            "evacuation_template": "Maintain at least {radius} meters from the affected area. Follow health authority guidelines.",
            "emergency_contacts": [
                {"service": "Public Health", "number": "999"},
                {"service": "Ambulance", "number": "999"},
                {"service": "Emergency Hotline", "number": "112"}
            ]
        },
        CrisisType.LANDSLIDE: {
            "playbook_id": "LANDSLIDE_STANDARD",
            "immediate_actions": [
                {
                    "priority": 1,
                    "action": "Evacuate immediately if on unstable ground",
                    "rationale": "Landslides can occur suddenly with little warning"
                },
                {
                    "priority": 2,
                    "action": "Move to higher, stable ground",
                    "rationale": "Landslides flow downhill and can travel far"
                },
                {
                    "priority": 3,
                    "action": "Alert others in the path of the landslide",
                    "rationale": "Early warning can save lives downstream"
                }
            ],
            "what_to_do": [
                "Listen for unusual sounds (trees cracking, boulders knocking)",
                "Watch for changes in water flow or sudden water increase",
                "Move perpendicular to the landslide path if possible",
                "Stay alert for additional slides",
                "Report landslides to authorities",
                "Avoid the area until declared safe"
            ],
            "what_not_to_do": [
                "Do not return to the area during heavy rain",
                "Do not cross damaged bridges or roads",
                "Do not ignore evacuation orders",
                "Do not assume the danger has passed after one slide",
                "Do not drive through areas with debris"
            ],
            "evacuation_template": "Move to stable ground at least {radius} meters from the slide area. Avoid valleys and low-lying areas.",
            "emergency_contacts": [
                {"service": "Disaster Management", "number": "999"},
                {"service": "Emergency Hotline", "number": "112"}
            ]
        },
        CrisisType.HAZARDOUS_SPILL: {
            "playbook_id": "HAZMAT_STANDARD",
            "immediate_actions": [
                {
                    "priority": 1,
                    "action": "Evacuate the area immediately",
                    "rationale": "Hazardous materials can cause serious injury or death"
                },
                {
                    "priority": 2,
                    "action": "Move upwind and uphill from the spill",
                    "rationale": "Toxic fumes travel downwind and liquids flow downhill"
                },
                {
                    "priority": 3,
                    "action": "Call emergency services with spill details",
                    "rationale": "Specialized hazmat teams need specific information to respond safely"
                }
            ],
            "what_to_do": [
                "Cover your nose and mouth with cloth",
                "Remove contaminated clothing if exposed",
                "Wash exposed skin with soap and water",
                "Seek medical attention if exposed",
                "Follow decontamination procedures if instructed",
                "Stay informed through official channels"
            ],
            "what_not_to_do": [
                "Do not touch or walk through spilled material",
                "Do not attempt to clean up the spill yourself",
                "Do not eat or drink anything from the area",
                "Do not return until authorities declare it safe",
                "Do not ignore symptoms of exposure"
            ],
            "evacuation_template": "Evacuate at least {radius} meters upwind from the spill. Follow hazmat team instructions.",
            "emergency_contacts": [
                {"service": "Disaster Management", "number": "999"},
                {"service": "Hazmat Team", "number": "999"},
                {"service": "Emergency Hotline", "number": "112"}
            ]
        },
        CrisisType.OTHER: {
            "playbook_id": "GENERAL_STANDARD",
            "immediate_actions": [
                {
                    "priority": 1,
                    "action": "Assess the situation and ensure your safety",
                    "rationale": "Understanding the threat helps you respond appropriately"
                },
                {
                    "priority": 2,
                    "action": "Call emergency services",
                    "rationale": "Professional help is essential for most emergencies"
                },
                {
                    "priority": 3,
                    "action": "Follow instructions from authorities",
                    "rationale": "Emergency responders have training and information you may not have"
                }
            ],
            "what_to_do": [
                "Stay calm and think clearly",
                "Help others if you can do so safely",
                "Document the situation if safe",
                "Follow official guidance",
                "Keep emergency contacts informed",
                "Stay informed through reliable sources"
            ],
            "what_not_to_do": [
                "Do not panic",
                "Do not put yourself in danger",
                "Do not spread unverified information",
                "Do not ignore official warnings",
                "Do not return to dangerous areas"
            ],
            "evacuation_template": "Move to a safe location at least {radius} meters from the incident. Follow official guidance.",
            "emergency_contacts": [
                {"service": "Emergency Services", "number": "999"},
                {"service": "Emergency Hotline", "number": "112"}
            ]
        }
    }
    
    # Risk level thresholds based on distance
    RISK_THRESHOLDS = {
        "IMMEDIATE": 500,    # Within 500m
        "HIGH": 1000,        # Within 1km
        "MODERATE": 2000,    # Within 2km
        "LOW": float('inf')  # Beyond 2km
    }
    
    def __init__(self):
        """Initialize advisory service."""
        self.watsonx = watsonx_service
        self.cloudant = cloudant_service
    
    def determine_risk_level(self, distance_meters: Optional[float], crisis_type: CrisisType) -> str:
        """
        Determine risk level based on distance and crisis type.
        
        Args:
            distance_meters: Distance from incident (None if unknown)
            crisis_type: Type of crisis
            
        Returns:
            Risk level: IMMEDIATE, HIGH, MODERATE, or LOW
        """
        if distance_meters is None:
            return "MODERATE"  # Default if location unknown
        
        # Crisis-specific adjustments
        multipliers = {
            CrisisType.FIRE: 1.0,
            CrisisType.FLOOD: 1.5,
            CrisisType.HAZARDOUS_SPILL: 1.5,
            CrisisType.WILDLIFE: 0.8,
            CrisisType.ACCIDENT: 0.5,
        }
        
        multiplier = multipliers.get(crisis_type, 1.0)
        adjusted_distance = distance_meters / multiplier
        
        if adjusted_distance <= self.RISK_THRESHOLDS["IMMEDIATE"]:
            return "IMMEDIATE"
        elif adjusted_distance <= self.RISK_THRESHOLDS["HIGH"]:
            return "HIGH"
        elif adjusted_distance <= self.RISK_THRESHOLDS["MODERATE"]:
            return "MODERATE"
        else:
            return "LOW"
    
    def get_playbook(self, crisis_type: CrisisType) -> Dict[str, Any]:
        """
        Get safety playbook for crisis type.
        
        Args:
            crisis_type: Type of crisis
            
        Returns:
            Safety playbook dictionary
        """
        return self.SAFETY_PLAYBOOKS.get(crisis_type, self.SAFETY_PLAYBOOKS[CrisisType.OTHER])
    
    def generate_primary_advice(
        self,
        crisis_type: CrisisType,
        risk_level: str,
        distance_meters: Optional[float]
    ) -> str:
        """
        Generate primary safety advice based on risk level.
        
        Args:
            crisis_type: Type of crisis
            risk_level: Risk level
            distance_meters: Distance from incident
            
        Returns:
            Primary advice string
        """
        crisis_name = crisis_type.value.replace("_", " ").title()
        
        if risk_level == "IMMEDIATE":
            if distance_meters:
                return f"IMMEDIATE DANGER: {crisis_name} incident within {int(distance_meters)}m. Evacuate immediately!"
            return f"IMMEDIATE DANGER: {crisis_name} incident nearby. Evacuate immediately!"
        elif risk_level == "HIGH":
            if distance_meters:
                return f"HIGH RISK: {crisis_name} incident {int(distance_meters)}m away. Prepare to evacuate and follow safety guidelines."
            return f"HIGH RISK: {crisis_name} incident in your area. Prepare to evacuate and follow safety guidelines."
        elif risk_level == "MODERATE":
            return f"MODERATE RISK: {crisis_name} incident reported in your area. Stay alert and follow safety precautions."
        else:
            return f"LOW RISK: {crisis_name} incident reported. Monitor the situation and stay informed."
    
    def enhance_with_ai(
        self,
        incident: Incident,
        playbook: Dict[str, Any],
        user_context: Optional[str],
        distance_meters: Optional[float]
    ) -> Optional[str]:
        """
        Use watsonx AI to enhance safety advice with context-specific recommendations.
        
        Args:
            incident: Incident object
            playbook: Base safety playbook
            user_context: User's context
            distance_meters: Distance from incident
            
        Returns:
            AI-enhanced advice or None if AI unavailable
        """
        if not self.watsonx.enabled:
            return None
        
        try:
            if not self.watsonx.model:
                return None
            
            prompt = self._build_advisory_prompt(incident, playbook, user_context, distance_meters)
            response = self.watsonx.model.generate_text(prompt=prompt)
            
            # Extract advice from response
            if response and len(response.strip()) > 20:
                return response.strip()
            
            return None
            
        except Exception as e:
            logger.error(f"AI enhancement failed: {e}")
            return None
    
    def _build_advisory_prompt(
        self,
        incident: Incident,
        playbook: Dict[str, Any],
        user_context: Optional[str],
        distance_meters: Optional[float]
    ) -> str:
        """Build prompt for AI-enhanced advisory."""
        
        context_str = f"User context: {user_context}" if user_context else "No specific user context provided"
        distance_str = f"{int(distance_meters)}m from incident" if distance_meters else "Unknown distance"
        
        prompt = f"""You are a safety advisory AI helping people during emergencies.

INCIDENT DETAILS:
- Type: {incident.crisis_type.value}
- Severity: {incident.severity.value}
- Location: {incident.location_description or 'Unknown'}
- Confidence: {incident.confidence_score:.1f}%
- {distance_str}
- {context_str}

BASE SAFETY ADVICE:
{playbook['immediate_actions'][0]['action']}

TASK:
Provide 2-3 sentences of additional context-specific safety advice. Be concise, actionable, and empathetic.
Focus on what the person should do RIGHT NOW given their specific situation.

Your advice:"""
        
        return prompt
    
    def generate_advisory(
        self,
        db: Session,
        incident_id: str,
        user_latitude: Optional[float] = None,
        user_longitude: Optional[float] = None,
        user_context: Optional[str] = None
    ) -> Optional[AdvisoryResponse]:
        """
        Generate safety advisory for an incident.
        
        Args:
            db: Database session
            incident_id: Incident ID
            user_latitude: User's latitude
            user_longitude: User's longitude
            user_context: User's context
            
        Returns:
            AdvisoryResponse or None if incident not found
        """
        agent_run_id = generate_agent_run_id("advisory")
        start_time = datetime.now()
        
        try:
            # Get incident
            incident = db.query(Incident).filter(Incident.id == incident_id).first()
            if not incident:
                logger.warning(f"Incident {incident_id} not found")
                return None
            
            # Calculate distance if user location provided
            distance_meters = None
            # Type cast to handle SQLAlchemy Column types
            incident_lat: float = incident.latitude  # type: ignore
            incident_lon: float = incident.longitude  # type: ignore
            if user_latitude is not None and user_longitude is not None:
                distance_meters = haversine_distance(
                    user_latitude, user_longitude,
                    incident_lat, incident_lon
                )
            
            # Get playbook - type cast crisis_type
            crisis_type: CrisisType = incident.crisis_type  # type: ignore
            playbook = self.get_playbook(crisis_type)
            
            # Determine risk level
            risk_level = self.determine_risk_level(distance_meters, crisis_type)
            
            # Generate primary advice
            primary_advice = self.generate_primary_advice(
                crisis_type,
                risk_level,
                distance_meters
            )
            
            # Try to enhance with AI
            ai_enhanced = False
            ai_advice = self.enhance_with_ai(incident, playbook, user_context, distance_meters)
            if ai_advice:
                primary_advice = f"{primary_advice}\n\n{ai_advice}"
                ai_enhanced = True
            
            # Build immediate actions
            immediate_actions = [
                SafetyAction(**action) for action in playbook["immediate_actions"]
            ]
            
            # Build evacuation advice
            evacuation_radius = 500 if risk_level == "IMMEDIATE" else 1000
            evacuation_advice = playbook["evacuation_template"].format(radius=evacuation_radius)
            
            # Create response - type cast for response
            incident_severity: SeverityLevel = incident.severity  # type: ignore
            response = AdvisoryResponse(
                incident_id=incident_id,
                crisis_type=crisis_type,
                severity=incident_severity,
                distance_meters=distance_meters,
                risk_level=risk_level,
                primary_advice=primary_advice,
                immediate_actions=immediate_actions,
                what_to_do=playbook["what_to_do"],
                what_not_to_do=playbook["what_not_to_do"],
                evacuation_advice=evacuation_advice,
                emergency_contacts=playbook["emergency_contacts"],
                generated_at=utc_now(),
                playbook_used=playbook["playbook_id"],
                ai_enhanced=ai_enhanced
            )
            
            # Log to Cloudant
            elapsed_ms = (datetime.now() - start_time).total_seconds() * 1000
            self._log_advisory(
                agent_run_id=agent_run_id,
                incident_id=incident_id,
                crisis_type=incident.crisis_type.value,
                risk_level=risk_level,
                distance_meters=distance_meters,
                ai_enhanced=ai_enhanced,
                elapsed_ms=elapsed_ms
            )
            
            logger.info(
                f"Generated {risk_level} advisory for incident {incident_id} "
                f"(AI enhanced: {ai_enhanced})"
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating advisory for incident {incident_id}: {e}")
            self._log_advisory(
                agent_run_id=agent_run_id,
                incident_id=incident_id,
                crisis_type=None,
                risk_level=None,
                distance_meters=None,
                ai_enhanced=False,
                elapsed_ms=None,
                error=str(e)
            )
            return None
    
    def _log_advisory(
        self,
        agent_run_id: str,
        incident_id: str,
        crisis_type: Optional[str],
        risk_level: Optional[str],
        distance_meters: Optional[float],
        ai_enhanced: bool,
        elapsed_ms: Optional[float],
        error: Optional[str] = None
    ) -> None:
        """
        Log advisory generation to Cloudant.
        
        Args:
            agent_run_id: Agent run ID
            incident_id: Incident ID
            crisis_type: Crisis type
            risk_level: Risk level
            distance_meters: Distance from incident
            ai_enhanced: Whether AI enhanced the advice
            elapsed_ms: Generation time in milliseconds
            error: Error message if failed
        """
        try:
            log_data = {
                "agent_run_id": agent_run_id,
                "agent_name": AgentName.ADVISORY_AGENT.value,
                "incident_id": incident_id,
                "crisis_type": crisis_type,
                "risk_level": risk_level,
                "distance_meters": distance_meters,
                "ai_enhanced": ai_enhanced,
                "elapsed_ms": elapsed_ms,
                "status": AgentRunStatus.FAILED.value if error else AgentRunStatus.SUCCESS.value,
                "error": error,
                "timestamp": utc_now().isoformat()
            }
            
            self.cloudant.store_agent_log(
                agent_run_id=agent_run_id,
                agent_type=AgentName.ADVISORY_AGENT.value,
                payload=log_data
            )
        except Exception as e:
            logger.error(f"Failed to log advisory to Cloudant: {e}")


# Singleton instance
advisory_service = AdvisoryService()

# Made with Bob