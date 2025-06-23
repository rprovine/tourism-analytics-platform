from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

from app.core.database import get_db
from app.services.lead_service import LeadService

router = APIRouter()


class LeadCreate(BaseModel):
    business_id: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    lead_source: Optional[str] = None
    interest_level: Optional[str] = None
    travel_dates: Optional[str] = None
    destination: Optional[str] = None
    party_size: Optional[int] = None
    budget_range: Optional[str] = None
    service_interests: Optional[List[str]] = None
    notes: Optional[str] = None


class LeadUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    lead_status: Optional[str] = None
    lead_score: Optional[int] = None
    interest_level: Optional[str] = None
    travel_dates: Optional[str] = None
    destination: Optional[str] = None
    party_size: Optional[int] = None
    budget_range: Optional[str] = None
    service_interests: Optional[List[str]] = None
    next_follow_up: Optional[datetime] = None
    notes: Optional[str] = None


class ActivityCreate(BaseModel):
    activity_type: str
    subject: Optional[str] = None
    description: Optional[str] = None
    activity_date: datetime
    duration_minutes: Optional[int] = None
    outcome: Optional[str] = None


@router.post("/")
async def create_lead(
    lead: LeadCreate,
    sync_to_hubspot: bool = Query(True, description="Sync to HubSpot"),
    db: AsyncSession = Depends(get_db)
):
    """Create a new lead"""
    try:
        result = await LeadService.create_lead(
            db=db,
            lead_data=lead.dict(),
            sync_to_hubspot=sync_to_hubspot
        )
        
        if result["status"] == "success":
            return {
                "status": "success",
                "message": "Lead created successfully",
                "lead_id": result["lead"].id,
                "hubspot_sync": result.get("hubspot_sync")
            }
        else:
            raise HTTPException(status_code=400, detail=result["message"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def get_leads(
    business_id: str = Query(..., description="Business ID"),
    status: Optional[str] = Query(None, description="Filter by lead status"),
    source: Optional[str] = Query(None, description="Filter by lead source"),
    limit: int = Query(100, le=1000),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """Get leads with optional filters"""
    try:
        leads = await LeadService.get_leads(
            db=db,
            business_id=business_id,
            status=status,
            source=source,
            limit=limit,
            offset=offset
        )
        
        return {
            "status": "success",
            "leads": [
                {
                    "id": lead.id,
                    "business_id": lead.business_id,
                    "email": lead.email,
                    "first_name": lead.first_name,
                    "last_name": lead.last_name,
                    "phone": lead.phone,
                    "company": lead.company,
                    "lead_source": lead.lead_source,
                    "lead_status": lead.lead_status,
                    "lead_score": lead.lead_score,
                    "interest_level": lead.interest_level,
                    "travel_dates": lead.travel_dates,
                    "destination": lead.destination,
                    "party_size": lead.party_size,
                    "budget_range": lead.budget_range,
                    "service_interests": lead.service_interests,
                    "last_contact_date": lead.last_contact_date,
                    "next_follow_up": lead.next_follow_up,
                    "converted": lead.converted,
                    "conversion_value": lead.conversion_value,
                    "synced_to_hubspot": lead.synced_to_hubspot,
                    "hubspot_contact_id": lead.hubspot_contact_id,
                    "created_at": lead.created_at,
                    "updated_at": lead.updated_at
                }
                for lead in leads
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{lead_id}")
async def get_lead(
    lead_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific lead by ID"""
    try:
        lead = await LeadService.get_lead_by_id(db, lead_id)
        
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        return {
            "status": "success",
            "lead": {
                "id": lead.id,
                "business_id": lead.business_id,
                "email": lead.email,
                "first_name": lead.first_name,
                "last_name": lead.last_name,
                "phone": lead.phone,
                "company": lead.company,
                "lead_source": lead.lead_source,
                "lead_status": lead.lead_status,
                "lead_score": lead.lead_score,
                "interest_level": lead.interest_level,
                "travel_dates": lead.travel_dates,
                "destination": lead.destination,
                "party_size": lead.party_size,
                "budget_range": lead.budget_range,
                "service_interests": lead.service_interests,
                "last_contact_date": lead.last_contact_date,
                "next_follow_up": lead.next_follow_up,
                "notes": lead.notes,
                "converted": lead.converted,
                "conversion_value": lead.conversion_value,
                "synced_to_hubspot": lead.synced_to_hubspot,
                "hubspot_contact_id": lead.hubspot_contact_id,
                "created_at": lead.created_at,
                "updated_at": lead.updated_at
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{lead_id}")
async def update_lead(
    lead_id: int,
    lead_update: LeadUpdate,
    sync_to_hubspot: bool = Query(True, description="Sync to HubSpot"),
    db: AsyncSession = Depends(get_db)
):
    """Update a lead"""
    try:
        # Only include non-None values
        update_data = {k: v for k, v in lead_update.dict().items() if v is not None}
        
        result = await LeadService.update_lead(
            db=db,
            lead_id=lead_id,
            update_data=update_data,
            sync_to_hubspot=sync_to_hubspot
        )
        
        if result["status"] == "success":
            return {
                "status": "success",
                "message": "Lead updated successfully",
                "lead_id": result["lead"].id,
                "hubspot_sync": result.get("hubspot_sync")
            }
        else:
            raise HTTPException(status_code=400, detail=result["message"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{lead_id}/activities")
async def add_lead_activity(
    lead_id: int,
    activity: ActivityCreate,
    sync_to_hubspot: bool = Query(True, description="Sync to HubSpot"),
    db: AsyncSession = Depends(get_db)
):
    """Add an activity to a lead"""
    try:
        result = await LeadService.add_lead_activity(
            db=db,
            lead_id=lead_id,
            activity_data=activity.dict(),
            sync_to_hubspot=sync_to_hubspot
        )
        
        if result["status"] == "success":
            return {
                "status": "success",
                "message": "Activity added successfully",
                "activity_id": result["activity"].id,
                "hubspot_sync": result.get("hubspot_sync")
            }
        else:
            raise HTTPException(status_code=400, detail=result["message"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{lead_id}/activities")
async def get_lead_activities(
    lead_id: int,
    limit: int = Query(50, le=200),
    db: AsyncSession = Depends(get_db)
):
    """Get activities for a lead"""
    try:
        activities = await LeadService.get_lead_activities(db, lead_id, limit)
        
        return {
            "status": "success",
            "activities": [
                {
                    "id": activity.id,
                    "lead_id": activity.lead_id,
                    "activity_type": activity.activity_type,
                    "subject": activity.subject,
                    "description": activity.description,
                    "activity_date": activity.activity_date,
                    "duration_minutes": activity.duration_minutes,
                    "outcome": activity.outcome,
                    "hubspot_activity_id": activity.hubspot_activity_id,
                    "created_at": activity.created_at
                }
                for activity in activities
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{lead_id}/convert")
async def convert_lead(
    lead_id: int,
    conversion_value: Optional[float] = Query(None, description="Conversion value"),
    create_deal: bool = Query(True, description="Create deal in HubSpot"),
    db: AsyncSession = Depends(get_db)
):
    """Convert a lead"""
    try:
        result = await LeadService.convert_lead(
            db=db,
            lead_id=lead_id,
            conversion_value=conversion_value,
            create_deal=create_deal
        )
        
        if result["status"] == "success":
            return {
                "status": "success",
                "message": "Lead converted successfully",
                "lead_id": result["lead"].id,
                "deal_created": result.get("deal_created")
            }
        else:
            raise HTTPException(status_code=400, detail=result["message"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/{business_id}")
async def get_lead_analytics(
    business_id: str,
    start_date: Optional[datetime] = Query(None, description="Start date"),
    end_date: Optional[datetime] = Query(None, description="End date"),
    db: AsyncSession = Depends(get_db)
):
    """Get lead analytics for a business"""
    try:
        analytics = await LeadService.get_lead_analytics(
            db, business_id, start_date, end_date
        )
        return analytics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sync/hubspot")
async def sync_leads_to_hubspot(
    business_id: str = Query(..., description="Business ID"),
    db: AsyncSession = Depends(get_db)
):
    """Sync all unsynced leads to HubSpot"""
    try:
        result = await LeadService.sync_all_leads_to_hubspot(db, business_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))