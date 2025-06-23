from typing import List, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, desc, or_
from datetime import datetime, timedelta
import json
import asyncio

from app.models.lead import Lead, LeadActivity, HubSpotSyncLog
from app.integrations.hubspot_client import hubspot_client


class LeadService:
    
    @staticmethod
    async def create_lead(
        db: AsyncSession,
        lead_data: Dict,
        sync_to_hubspot: bool = True
    ) -> Dict:
        """
        Create a new lead and optionally sync to HubSpot
        """
        try:
            # Check if lead with email already exists
            existing_lead_query = select(Lead).where(Lead.email == lead_data["email"])
            existing_result = await db.execute(existing_lead_query)
            existing_lead = existing_result.scalar_one_or_none()
            
            if existing_lead:
                return {
                    "status": "error",
                    "message": "Lead with this email already exists",
                    "existing_lead_id": existing_lead.id
                }
            
            # Create lead in database
            lead = Lead(**lead_data)
            db.add(lead)
            await db.commit()
            await db.refresh(lead)
            
            # Sync to HubSpot if enabled
            hubspot_result = None
            if sync_to_hubspot:
                hubspot_result = await LeadService._sync_lead_to_hubspot(db, lead)
            
            return {
                "status": "success",
                "lead": lead,
                "hubspot_sync": hubspot_result
            }
            
        except Exception as e:
            await db.rollback()
            return {
                "status": "error",
                "message": f"Lead creation failed: {str(e)}"
            }
    
    @staticmethod
    async def update_lead(
        db: AsyncSession,
        lead_id: int,
        update_data: Dict,
        sync_to_hubspot: bool = True
    ) -> Dict:
        """
        Update an existing lead and optionally sync to HubSpot
        """
        try:
            # Get the lead
            lead_query = select(Lead).where(Lead.id == lead_id)
            lead_result = await db.execute(lead_query)
            lead = lead_result.scalar_one_or_none()
            
            if not lead:
                return {
                    "status": "error",
                    "message": "Lead not found"
                }
            
            # Update lead fields
            for field, value in update_data.items():
                if hasattr(lead, field):
                    setattr(lead, field, value)
            
            lead.updated_at = datetime.now()
            await db.commit()
            await db.refresh(lead)
            
            # Sync to HubSpot if enabled and lead is already synced
            hubspot_result = None
            if sync_to_hubspot and lead.hubspot_contact_id:
                hubspot_result = await LeadService._update_hubspot_contact(db, lead, update_data)
            
            return {
                "status": "success",
                "lead": lead,
                "hubspot_sync": hubspot_result
            }
            
        except Exception as e:
            await db.rollback()
            return {
                "status": "error",
                "message": f"Lead update failed: {str(e)}"
            }
    
    @staticmethod
    async def get_leads(
        db: AsyncSession,
        business_id: str,
        status: Optional[str] = None,
        source: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Lead]:
        """
        Get leads with filters
        """
        query = select(Lead).where(Lead.business_id == business_id)
        
        if status:
            query = query.where(Lead.lead_status == status)
        
        if source:
            query = query.where(Lead.lead_source == source)
        
        query = query.order_by(desc(Lead.created_at)).limit(limit).offset(offset)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def get_lead_by_id(db: AsyncSession, lead_id: int) -> Optional[Lead]:
        """
        Get a lead by ID
        """
        query = select(Lead).where(Lead.id == lead_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def add_lead_activity(
        db: AsyncSession,
        lead_id: int,
        activity_data: Dict,
        sync_to_hubspot: bool = True
    ) -> Dict:
        """
        Add an activity to a lead
        """
        try:
            # Get the lead
            lead = await LeadService.get_lead_by_id(db, lead_id)
            if not lead:
                return {
                    "status": "error",
                    "message": "Lead not found"
                }
            
            # Create activity
            activity = LeadActivity(
                lead_id=lead_id,
                **activity_data
            )
            
            db.add(activity)
            await db.commit()
            await db.refresh(activity)
            
            # Update lead's last contact date
            lead.last_contact_date = activity.activity_date
            await db.commit()
            
            # Sync to HubSpot if enabled
            hubspot_result = None
            if sync_to_hubspot and lead.hubspot_contact_id:
                hubspot_result = await LeadService._sync_activity_to_hubspot(db, lead, activity)
            
            return {
                "status": "success",
                "activity": activity,
                "hubspot_sync": hubspot_result
            }
            
        except Exception as e:
            await db.rollback()
            return {
                "status": "error",
                "message": f"Activity creation failed: {str(e)}"
            }
    
    @staticmethod
    async def get_lead_activities(
        db: AsyncSession,
        lead_id: int,
        limit: int = 50
    ) -> List[LeadActivity]:
        """
        Get activities for a lead
        """
        query = select(LeadActivity).where(
            LeadActivity.lead_id == lead_id
        ).order_by(desc(LeadActivity.activity_date)).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def convert_lead(
        db: AsyncSession,
        lead_id: int,
        conversion_value: Optional[float] = None,
        create_deal: bool = True
    ) -> Dict:
        """
        Mark a lead as converted and optionally create a deal in HubSpot
        """
        try:
            # Get the lead
            lead = await LeadService.get_lead_by_id(db, lead_id)
            if not lead:
                return {
                    "status": "error",
                    "message": "Lead not found"
                }
            
            # Update lead status
            lead.converted = True
            lead.conversion_date = datetime.now()
            lead.lead_status = "converted"
            
            if conversion_value:
                lead.conversion_value = conversion_value
            
            await db.commit()
            
            # Create deal in HubSpot if enabled
            deal_result = None
            if create_deal and lead.hubspot_contact_id:
                deal_data = {
                    "name": f"Tourism Booking - {lead.first_name} {lead.last_name}",
                    "contact_id": lead.hubspot_contact_id,
                    "value": conversion_value,
                    "stage": "closedwon",
                    "close_date": datetime.now().isoformat()
                }
                deal_result = await hubspot_client.create_deal(deal_data)
            
            return {
                "status": "success",
                "lead": lead,
                "deal_created": deal_result
            }
            
        except Exception as e:
            await db.rollback()
            return {
                "status": "error",
                "message": f"Lead conversion failed: {str(e)}"
            }
    
    @staticmethod
    async def get_lead_analytics(
        db: AsyncSession,
        business_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict:
        """
        Get lead analytics for a business
        """
        try:
            # Set default date range
            if not end_date:
                end_date = datetime.now()
            if not start_date:
                start_date = end_date - timedelta(days=30)
            
            # Base query
            base_query = select(Lead).where(
                and_(
                    Lead.business_id == business_id,
                    Lead.created_at >= start_date,
                    Lead.created_at <= end_date
                )
            )
            
            # Total leads
            total_result = await db.execute(
                select(func.count(Lead.id)).select_from(base_query.subquery())
            )
            total_leads = total_result.scalar()
            
            # Leads by status
            status_query = select(Lead.lead_status, func.count(Lead.id)).where(
                and_(
                    Lead.business_id == business_id,
                    Lead.created_at >= start_date,
                    Lead.created_at <= end_date
                )
            ).group_by(Lead.lead_status)
            
            status_result = await db.execute(status_query)
            status_distribution = dict(status_result.fetchall())
            
            # Leads by source
            source_query = select(Lead.lead_source, func.count(Lead.id)).where(
                and_(
                    Lead.business_id == business_id,
                    Lead.created_at >= start_date,
                    Lead.created_at <= end_date
                )
            ).group_by(Lead.lead_source)
            
            source_result = await db.execute(source_query)
            source_distribution = dict(source_result.fetchall())
            
            # Conversion metrics
            converted_count_result = await db.execute(
                select(func.count(Lead.id)).where(
                    and_(
                        Lead.business_id == business_id,
                        Lead.converted == True,
                        Lead.conversion_date >= start_date,
                        Lead.conversion_date <= end_date
                    )
                )
            )
            converted_count = converted_count_result.scalar()
            
            # Total conversion value
            conversion_value_result = await db.execute(
                select(func.sum(Lead.conversion_value)).where(
                    and_(
                        Lead.business_id == business_id,
                        Lead.converted == True,
                        Lead.conversion_date >= start_date,
                        Lead.conversion_date <= end_date
                    )
                )
            )
            total_conversion_value = conversion_value_result.scalar() or 0
            
            # Calculate conversion rate
            conversion_rate = (converted_count / total_leads * 100) if total_leads > 0 else 0
            
            # Average lead score
            avg_score_result = await db.execute(
                select(func.avg(Lead.lead_score)).select_from(base_query.subquery())
            )
            avg_lead_score = avg_score_result.scalar() or 0
            
            return {
                "status": "success",
                "analytics": {
                    "total_leads": total_leads,
                    "converted_leads": converted_count,
                    "conversion_rate": round(conversion_rate, 2),
                    "total_conversion_value": total_conversion_value,
                    "average_lead_score": round(avg_lead_score, 1),
                    "status_distribution": status_distribution,
                    "source_distribution": source_distribution,
                    "date_range": {
                        "start": start_date.isoformat(),
                        "end": end_date.isoformat()
                    }
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Analytics calculation failed: {str(e)}"
            }
    
    @staticmethod
    async def sync_all_leads_to_hubspot(db: AsyncSession, business_id: str) -> Dict:
        """
        Sync all unsynced leads to HubSpot
        """
        try:
            # Get unsynced leads
            unsynced_query = select(Lead).where(
                and_(
                    Lead.business_id == business_id,
                    Lead.synced_to_hubspot == False
                )
            )
            
            unsynced_result = await db.execute(unsynced_query)
            unsynced_leads = unsynced_result.scalars().all()
            
            sync_results = {
                "total_leads": len(unsynced_leads),
                "successful": 0,
                "failed": 0,
                "errors": []
            }
            
            for lead in unsynced_leads:
                try:
                    result = await LeadService._sync_lead_to_hubspot(db, lead)
                    if result and result.get("status") == "success":
                        sync_results["successful"] += 1
                    else:
                        sync_results["failed"] += 1
                        sync_results["errors"].append({
                            "lead_id": lead.id,
                            "error": result.get("message", "Unknown error") if result else "No response"
                        })
                except Exception as e:
                    sync_results["failed"] += 1
                    sync_results["errors"].append({
                        "lead_id": lead.id,
                        "error": str(e)
                    })
                
                # Add delay to respect rate limits
                await asyncio.sleep(0.1)
            
            return {
                "status": "success",
                "sync_results": sync_results
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Bulk sync failed: {str(e)}"
            }
    
    @staticmethod
    async def _sync_lead_to_hubspot(db: AsyncSession, lead: Lead) -> Optional[Dict]:
        """
        Sync a single lead to HubSpot
        """
        try:
            # Check if contact already exists in HubSpot
            search_result = await hubspot_client.search_contacts(lead.email)
            
            if search_result.get("status") == "success" and search_result.get("total", 0) > 0:
                # Contact exists, update it
                existing_contact = search_result["contacts"][0]
                hubspot_contact_id = existing_contact["id"]
                
                update_data = {
                    "first_name": lead.first_name,
                    "last_name": lead.last_name,
                    "phone": lead.phone,
                    "company": lead.company,
                    "lead_status": lead.lead_status,
                    "lead_score": lead.lead_score,
                    "travel_dates": lead.travel_dates,
                    "destination": lead.destination,
                    "party_size": lead.party_size,
                    "budget_range": lead.budget_range,
                    "service_interests": lead.service_interests
                }
                
                result = await hubspot_client.update_contact(hubspot_contact_id, update_data)
            else:
                # Create new contact
                contact_data = {
                    "email": lead.email,
                    "first_name": lead.first_name,
                    "last_name": lead.last_name,
                    "phone": lead.phone,
                    "company": lead.company,
                    "lead_status": lead.lead_status,
                    "lead_score": lead.lead_score,
                    "travel_dates": lead.travel_dates,
                    "destination": lead.destination,
                    "party_size": lead.party_size,
                    "budget_range": lead.budget_range,
                    "service_interests": lead.service_interests
                }
                
                result = await hubspot_client.create_contact(contact_data)
                hubspot_contact_id = result.get("contact_id") if result.get("status") == "success" else None
            
            # Update lead with HubSpot info
            if result.get("status") == "success":
                lead.hubspot_contact_id = hubspot_contact_id
                lead.synced_to_hubspot = True
                lead.last_hubspot_sync = datetime.now()
                lead.hubspot_sync_error = None
            else:
                lead.hubspot_sync_error = result.get("message", "Unknown error")
            
            await db.commit()
            
            # Log the sync
            sync_log = HubSpotSyncLog(
                sync_type="lead",
                record_id=lead.id,
                hubspot_id=hubspot_contact_id,
                sync_status="success" if result.get("status") == "success" else "error",
                sync_direction="to_hubspot",
                error_message=result.get("message") if result.get("status") != "success" else None
            )
            db.add(sync_log)
            await db.commit()
            
            return result
            
        except Exception as e:
            # Log the error
            sync_log = HubSpotSyncLog(
                sync_type="lead",
                record_id=lead.id,
                sync_status="error",
                sync_direction="to_hubspot",
                error_message=str(e)
            )
            db.add(sync_log)
            await db.commit()
            
            return {
                "status": "error",
                "message": str(e)
            }
    
    @staticmethod
    async def _update_hubspot_contact(db: AsyncSession, lead: Lead, update_data: Dict) -> Optional[Dict]:
        """
        Update a HubSpot contact
        """
        try:
            result = await hubspot_client.update_contact(lead.hubspot_contact_id, update_data)
            
            if result.get("status") == "success":
                lead.last_hubspot_sync = datetime.now()
                lead.hubspot_sync_error = None
            else:
                lead.hubspot_sync_error = result.get("message", "Unknown error")
            
            await db.commit()
            return result
            
        except Exception as e:
            lead.hubspot_sync_error = str(e)
            await db.commit()
            return {
                "status": "error",
                "message": str(e)
            }
    
    @staticmethod
    async def _sync_activity_to_hubspot(db: AsyncSession, lead: Lead, activity: LeadActivity) -> Optional[Dict]:
        """
        Sync an activity to HubSpot
        """
        try:
            activity_data = {
                "activity_type": activity.activity_type,
                "subject": activity.subject,
                "description": activity.description,
                "activity_date": activity.activity_date,
                "duration_minutes": activity.duration_minutes,
                "outcome": activity.outcome
            }
            
            result = await hubspot_client.create_activity(lead.hubspot_contact_id, activity_data)
            
            if result.get("status") == "success":
                activity.hubspot_activity_id = result.get("activity_id")
                await db.commit()
            
            return result
            
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }