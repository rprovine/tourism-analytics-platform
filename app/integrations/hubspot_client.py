import asyncio
from typing import Dict, List, Optional, Any
import httpx
from datetime import datetime
import json
from app.core.config import settings
from app.core.redis_client import redis_client
import logging

logger = logging.getLogger(__name__)


class HubSpotClient:
    def __init__(self):
        self.api_key = settings.HUBSPOT_API_KEY
        self.portal_id = settings.HUBSPOT_PORTAL_ID
        self.base_url = "https://api.hubapi.com"
        self.rate_limit_delay = 0.1  # 10 requests per second max
        
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        json_data: Optional[Dict] = None,
        headers: Optional[Dict] = None
    ) -> Dict:
        """
        Make authenticated request to HubSpot API
        """
        if not self.api_key:
            raise ValueError("HubSpot API key not configured")
        
        url = f"{self.base_url}{endpoint}"
        
        default_headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        if headers:
            default_headers.update(headers)
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Rate limiting
                await asyncio.sleep(self.rate_limit_delay)
                
                response = await client.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json_data,
                    headers=default_headers
                )
                
                if response.status_code == 429:
                    # Rate limited, wait and retry
                    retry_after = int(response.headers.get('Retry-After', 1))
                    await asyncio.sleep(retry_after)
                    return await self._make_request(method, endpoint, params, json_data, headers)
                
                response.raise_for_status()
                return response.json()
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HubSpot API error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"HubSpot request error: {e}")
            raise
    
    async def create_contact(self, contact_data: Dict) -> Dict:
        """
        Create a new contact in HubSpot
        """
        try:
            # Prepare contact properties
            properties = {
                "email": contact_data.get("email"),
                "firstname": contact_data.get("first_name"),
                "lastname": contact_data.get("last_name"),
                "phone": contact_data.get("phone"),
                "company": contact_data.get("company"),
                "hs_lead_status": contact_data.get("lead_status", "NEW"),
                "hubspotscore": contact_data.get("lead_score", 0),
                "lifecyclestage": "lead"
            }
            
            # Add custom properties for tourism business
            if contact_data.get("travel_dates"):
                properties["travel_dates"] = contact_data["travel_dates"]
            
            if contact_data.get("destination"):
                properties["destination"] = contact_data["destination"]
            
            if contact_data.get("party_size"):
                properties["party_size"] = str(contact_data["party_size"])
            
            if contact_data.get("budget_range"):
                properties["budget_range"] = contact_data["budget_range"]
            
            if contact_data.get("service_interests"):
                properties["service_interests"] = json.dumps(contact_data["service_interests"])
            
            # Remove None values
            properties = {k: v for k, v in properties.items() if v is not None}
            
            payload = {"properties": properties}
            
            result = await self._make_request(
                "POST",
                "/crm/v3/objects/contacts",
                json_data=payload
            )
            
            return {
                "status": "success",
                "contact_id": result["id"],
                "contact_data": result
            }
            
        except Exception as e:
            logger.error(f"Create contact error: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def update_contact(self, contact_id: str, update_data: Dict) -> Dict:
        """
        Update an existing contact in HubSpot
        """
        try:
            # Prepare update properties
            properties = {}
            
            field_mapping = {
                "first_name": "firstname",
                "last_name": "lastname",
                "phone": "phone",
                "company": "company",
                "lead_status": "hs_lead_status",
                "lead_score": "hubspotscore"
            }
            
            for local_field, hubspot_field in field_mapping.items():
                if local_field in update_data and update_data[local_field] is not None:
                    properties[hubspot_field] = update_data[local_field]
            
            # Handle custom fields
            if "travel_dates" in update_data:
                properties["travel_dates"] = update_data["travel_dates"]
            
            if "destination" in update_data:
                properties["destination"] = update_data["destination"]
            
            if "party_size" in update_data:
                properties["party_size"] = str(update_data["party_size"])
            
            if "budget_range" in update_data:
                properties["budget_range"] = update_data["budget_range"]
            
            if "service_interests" in update_data:
                properties["service_interests"] = json.dumps(update_data["service_interests"])
            
            if not properties:
                return {"status": "success", "message": "No fields to update"}
            
            payload = {"properties": properties}
            
            result = await self._make_request(
                "PATCH",
                f"/crm/v3/objects/contacts/{contact_id}",
                json_data=payload
            )
            
            return {
                "status": "success",
                "contact_id": result["id"],
                "contact_data": result
            }
            
        except Exception as e:
            logger.error(f"Update contact error: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def get_contact(self, contact_id: str) -> Dict:
        """
        Get a contact from HubSpot
        """
        try:
            result = await self._make_request(
                "GET",
                f"/crm/v3/objects/contacts/{contact_id}"
            )
            
            return {
                "status": "success",
                "contact_data": result
            }
            
        except Exception as e:
            logger.error(f"Get contact error: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def search_contacts(self, email: str) -> Dict:
        """
        Search for contacts by email
        """
        try:
            payload = {
                "filterGroups": [
                    {
                        "filters": [
                            {
                                "propertyName": "email",
                                "operator": "EQ",
                                "value": email
                            }
                        ]
                    }
                ]
            }
            
            result = await self._make_request(
                "POST",
                "/crm/v3/objects/contacts/search",
                json_data=payload
            )
            
            return {
                "status": "success",
                "contacts": result.get("results", []),
                "total": result.get("total", 0)
            }
            
        except Exception as e:
            logger.error(f"Search contacts error: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def create_activity(self, contact_id: str, activity_data: Dict) -> Dict:
        """
        Create an activity (note, email, call, etc.) for a contact
        """
        try:
            # Map activity types to HubSpot engagement types
            activity_type_mapping = {
                "note": "NOTE",
                "email": "EMAIL",
                "call": "CALL",
                "meeting": "MEETING",
                "task": "TASK"
            }
            
            activity_type = activity_data.get("activity_type", "note")
            hubspot_type = activity_type_mapping.get(activity_type, "NOTE")
            
            # Prepare engagement data
            engagement_data = {
                "engagement": {
                    "active": True,
                    "type": hubspot_type,
                    "timestamp": int(activity_data.get("activity_date", datetime.now()).timestamp() * 1000)
                },
                "associations": {
                    "contactIds": [int(contact_id)]
                },
                "metadata": {
                    "body": activity_data.get("description", ""),
                    "subject": activity_data.get("subject", "")
                }
            }
            
            # Add type-specific metadata
            if hubspot_type == "CALL":
                engagement_data["metadata"]["duration"] = activity_data.get("duration_minutes", 0) * 60000  # Convert to milliseconds
                engagement_data["metadata"]["disposition"] = activity_data.get("outcome", "")
            
            result = await self._make_request(
                "POST",
                "/engagements/v1/engagements",
                json_data=engagement_data
            )
            
            return {
                "status": "success",
                "activity_id": result["engagement"]["id"],
                "activity_data": result
            }
            
        except Exception as e:
            logger.error(f"Create activity error: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def get_contact_activities(self, contact_id: str, limit: int = 100) -> Dict:
        """
        Get activities for a contact
        """
        try:
            params = {
                "objectId": contact_id,
                "objectType": "CONTACT",
                "limit": limit
            }
            
            result = await self._make_request(
                "GET",
                "/engagements/v1/engagements/associated/CONTACT/paged",
                params=params
            )
            
            return {
                "status": "success",
                "activities": result.get("results", []),
                "has_more": result.get("hasMore", False),
                "offset": result.get("offset", 0)
            }
            
        except Exception as e:
            logger.error(f"Get contact activities error: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def create_deal(self, deal_data: Dict) -> Dict:
        """
        Create a deal in HubSpot
        """
        try:
            properties = {
                "dealname": deal_data.get("name"),
                "amount": deal_data.get("value"),
                "dealstage": deal_data.get("stage", "appointmentscheduled"),
                "pipeline": deal_data.get("pipeline", "default"),
                "closedate": deal_data.get("close_date")
            }
            
            # Remove None values
            properties = {k: v for k, v in properties.items() if v is not None}
            
            payload = {"properties": properties}
            
            # If contact_id is provided, associate the deal
            if deal_data.get("contact_id"):
                payload["associations"] = [
                    {
                        "to": {"id": deal_data["contact_id"]},
                        "types": [{"associationCategory": "HUBSPOT_DEFINED", "associationTypeId": 3}]
                    }
                ]
            
            result = await self._make_request(
                "POST",
                "/crm/v3/objects/deals",
                json_data=payload
            )
            
            return {
                "status": "success",
                "deal_id": result["id"],
                "deal_data": result
            }
            
        except Exception as e:
            logger.error(f"Create deal error: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def get_pipeline_stages(self) -> Dict:
        """
        Get available pipeline stages
        """
        try:
            result = await self._make_request(
                "GET",
                "/crm/v3/pipelines/deals"
            )
            
            return {
                "status": "success",
                "pipelines": result.get("results", [])
            }
            
        except Exception as e:
            logger.error(f"Get pipeline stages error: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def test_connection(self) -> Dict:
        """
        Test the HubSpot API connection
        """
        try:
            result = await self._make_request(
                "GET",
                "/crm/v3/properties/contacts"
            )
            
            return {
                "status": "success",
                "message": "HubSpot connection successful",
                "properties_count": len(result.get("results", []))
            }
            
        except Exception as e:
            logger.error(f"HubSpot connection test failed: {e}")
            return {
                "status": "error",
                "message": f"Connection failed: {str(e)}"
            }


# Global instance
hubspot_client = HubSpotClient()