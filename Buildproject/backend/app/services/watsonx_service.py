"""
IBM watsonx.ai service for AI-powered report analysis.
Provides credibility scoring, crisis categorization, and decision recommendations.
"""

from typing import Dict, Any, Optional
import logging
import json
from ibm_watsonx_ai import APIClient, Credentials
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams

from app.core.config import settings
from app.schemas.common import CrisisType

logger = logging.getLogger(__name__)


class WatsonxService:
    """Service for IBM watsonx.ai operations."""
    
    def __init__(self):
        """Initialize watsonx.ai client if enabled."""
        self.enabled = settings.WATSONX_ENABLED
        self.client: Optional[APIClient] = None
        self.model: Optional[ModelInference] = None
        
        if self.enabled:
            try:
                # Create credentials
                credentials = Credentials(
                    url=settings.WATSONX_URL,
                    api_key=settings.WATSONX_API_KEY
                )
                
                # Create API client
                self.client = APIClient(credentials)
                
                # Initialize model
                self.model = ModelInference(
                    model_id=settings.WATSONX_MODEL_ID,
                    api_client=self.client,
                    project_id=settings.WATSONX_PROJECT_ID,
                    params={
                        GenParams.DECODING_METHOD: "greedy",
                        GenParams.MAX_NEW_TOKENS: 500,
                        GenParams.MIN_NEW_TOKENS: 50,
                        GenParams.TEMPERATURE: 0.3,
                        GenParams.TOP_K: 50,
                        GenParams.TOP_P: 0.9,
                    }
                )
                
                logger.info("watsonx.ai service initialized successfully")
                
            except Exception as e:
                logger.error(f"Failed to initialize watsonx.ai service: {e}")
                self.enabled = False
                self.client = None
                self.model = None
    
    def analyze_report(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a crisis report using watsonx.ai.
        
        Args:
            report_data: Dictionary containing report information:
                - crisis_type: Type of crisis
                - description: Report description
                - latitude: Location latitude
                - longitude: Location longitude
                - location_text: Human-readable location
                - image_url: Optional image URL
                - video_url: Optional video URL
                
        Returns:
            Dictionary with analysis results:
                - credibility_score: 0-100
                - crisis_category: Validated CrisisType
                - severity_score: 0-100
                - urgency_level: LOW, MEDIUM, HIGH, CRITICAL
                - recommended_action: String recommendation
                - reasoning: Explanation of the decision
        """
        if not self.enabled or not self.model:
            logger.warning("watsonx.ai not enabled, using fallback analysis")
            return self._fallback_analysis(report_data)
        
        try:
            # Build prompt for watsonx.ai
            prompt = self._build_analysis_prompt(report_data)
            
            # Generate response
            response = self.model.generate_text(prompt=prompt)
            
            # Parse response
            analysis = self._parse_analysis_response(response, report_data)
            
            logger.info(f"watsonx.ai analysis complete: credibility={analysis['credibility_score']}")
            
            return analysis
            
        except Exception as e:
            logger.error(f"watsonx.ai analysis failed: {e}")
            return self._fallback_analysis(report_data)
    
    def _build_analysis_prompt(self, report_data: Dict[str, Any]) -> str:
        """
        Build analysis prompt for watsonx.ai.
        
        Args:
            report_data: Report information
            
        Returns:
            Formatted prompt string
        """
        crisis_type = report_data.get("crisis_type", "UNKNOWN")
        description = report_data.get("description", "")
        location = report_data.get("location_text", "Unknown location")
        has_media = bool(report_data.get("image_url") or report_data.get("video_url"))
        
        prompt = f"""You are an AI crisis verification agent analyzing emergency reports.

REPORT DETAILS:
- Crisis Type: {crisis_type}
- Description: {description}
- Location: {location}
- Has Media Evidence: {has_media}

TASK:
Analyze this crisis report and provide a structured assessment in JSON format.

RESPONSE FORMAT (JSON only, no additional text):
{{
    "credibility_score": <0-100>,
    "crisis_category": "<FIRE|FLOOD|WILDLIFE|ACCIDENT|SECURITY|HEALTH|LANDSLIDE|HAZARDOUS_SPILL|OTHER>",
    "severity_score": <0-100>,
    "urgency_level": "<LOW|MEDIUM|HIGH|CRITICAL>",
    "recommended_action": "<brief action recommendation>",
    "reasoning": "<brief explanation of your assessment>"
}}

SCORING GUIDELINES:
- Credibility (0-100): Assess report authenticity based on description detail, consistency, and media presence
- Severity (0-100): Evaluate potential impact and danger level
- Urgency: LOW (<40), MEDIUM (40-60), HIGH (60-85), CRITICAL (>85)

Provide your analysis:"""
        
        return prompt
    
    def _parse_analysis_response(
        self,
        response: str,
        report_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Parse watsonx.ai response into structured format.
        
        Args:
            response: Raw response from watsonx.ai
            report_data: Original report data for fallback
            
        Returns:
            Structured analysis dictionary
        """
        try:
            # Try to extract JSON from response
            response = response.strip()
            
            # Find JSON object in response
            start_idx = response.find("{")
            end_idx = response.rfind("}") + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                analysis = json.loads(json_str)
                
                # Validate and normalize
                return self._validate_analysis(analysis, report_data)
            else:
                logger.warning("No JSON found in watsonx.ai response")
                return self._fallback_analysis(report_data)
                
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse watsonx.ai response: {e}")
            return self._fallback_analysis(report_data)
    
    def _validate_analysis(
        self,
        analysis: Dict[str, Any],
        report_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate and normalize analysis results.
        
        Args:
            analysis: Parsed analysis from watsonx.ai
            report_data: Original report data
            
        Returns:
            Validated and normalized analysis
        """
        # Validate credibility_score
        credibility = float(analysis.get("credibility_score", 50))
        credibility = max(0, min(100, credibility))
        
        # Validate severity_score
        severity = float(analysis.get("severity_score", 50))
        severity = max(0, min(100, severity))
        
        # Validate crisis_category
        crisis_category = analysis.get("crisis_category", report_data.get("crisis_type", "OTHER"))
        try:
            # Ensure it's a valid CrisisType
            CrisisType(crisis_category)
        except ValueError:
            crisis_category = report_data.get("crisis_type", "OTHER")
        
        # Validate urgency_level
        urgency = analysis.get("urgency_level", "MEDIUM").upper()
        if urgency not in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]:
            # Derive from severity
            if severity >= 85:
                urgency = "CRITICAL"
            elif severity >= 60:
                urgency = "HIGH"
            elif severity >= 40:
                urgency = "MEDIUM"
            else:
                urgency = "LOW"
        
        return {
            "credibility_score": credibility,
            "crisis_category": crisis_category,
            "severity_score": severity,
            "urgency_level": urgency,
            "recommended_action": analysis.get("recommended_action", "Verify and monitor situation"),
            "reasoning": analysis.get("reasoning", "AI analysis completed")
        }
    
    def _fallback_analysis(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Provide fallback analysis when watsonx.ai is unavailable.
        Uses rule-based heuristics.
        
        Args:
            report_data: Report information
            
        Returns:
            Fallback analysis results
        """
        crisis_type = report_data.get("crisis_type", "OTHER")
        description = report_data.get("description", "")
        has_media = bool(report_data.get("image_url") or report_data.get("video_url"))
        
        # Base credibility on description length and media presence
        base_credibility = 50
        if len(description) > 50:
            base_credibility += 10
        if len(description) > 100:
            base_credibility += 10
        if has_media:
            base_credibility += 15
        
        # Crisis-specific severity mapping
        severity_map = {
            "FIRE": 75,
            "FLOOD": 70,
            "WILDLIFE": 60,
            "ACCIDENT": 65,
            "SECURITY": 70,
            "HEALTH": 75,
            "LANDSLIDE": 80,
            "HAZARDOUS_SPILL": 85,
            "OTHER": 50
        }
        
        severity = severity_map.get(crisis_type, 50)
        
        # Determine urgency from severity
        if severity >= 85:
            urgency = "CRITICAL"
            action = "Immediate dispatch required"
        elif severity >= 70:
            urgency = "HIGH"
            action = "Rapid verification and potential dispatch"
        elif severity >= 50:
            urgency = "MEDIUM"
            action = "Standard verification process"
        else:
            urgency = "LOW"
            action = "Monitor and verify"
        
        logger.info(f"Using fallback analysis for {crisis_type}")
        
        return {
            "credibility_score": min(100, base_credibility),
            "crisis_category": crisis_type,
            "severity_score": severity,
            "urgency_level": urgency,
            "recommended_action": action,
            "reasoning": "Fallback rule-based analysis (watsonx.ai unavailable)"
        }


# Global instance
watsonx_service = WatsonxService()

# Made with Bob
