#!/usr/bin/env python3
"""
BigQuery CRUD operations for Company model
"""

import logging
from typing import List, Optional, Dict, Any
from app.crud.bigquery_crud import BigQueryCRUDBase
from google.cloud import bigquery

logger = logging.getLogger(__name__)


class BigQueryCompanyCRUD(BigQueryCRUDBase):
    """BigQuery CRUD operations for Company model"""
    
    def __init__(self):
        super().__init__(table_name="companies")
    
    async def get_by_vat(self, vat: str) -> Optional[Dict[str, Any]]:
        """Get company by VAT number"""
        return await self.get_by_id(vat, id_field="vat")
    
    async def get_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get company by name"""
        try:
            results = await self.get_multi(filters={"name": name}, limit=1)
            return results[0] if results else None
        except Exception as e:
            logger.error(f"❌ BigQuery get_by_name failed: {e}")
            return None
    
    async def create_company(self, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new company"""
        try:
            # Ensure VAT is present
            if 'vat' not in company_data:
                raise ValueError("VAT number is required")
            
            # Check if company already exists
            existing = await self.get_by_vat(company_data['vat'])
            if existing:
                logger.warning(f"Company with VAT {company_data['vat']} already exists")
                return existing
            
            # Create company
            result = await self.create(company_data)
            logger.info(f"✅ Created company: {company_data.get('name', 'Unknown')}")
            return result
            
        except Exception as e:
            logger.error(f"❌ BigQuery create_company failed: {e}")
            raise
    
    async def update_company(self, vat: str, company_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update company by VAT"""
        try:
            # Check if company exists
            existing = await self.get_by_vat(vat)
            if not existing:
                logger.warning(f"Company with VAT {vat} not found")
                return None
            
            # Update company
            result = await self.update(vat, company_data, id_field="vat")
            logger.info(f"✅ Updated company: {company_data.get('name', 'Unknown')}")
            return result
            
        except Exception as e:
            logger.error(f"❌ BigQuery update_company failed: {e}")
            return None
    
    async def list_companies(
        self, 
        skip: int = 0, 
        limit: int = 100,
        sector: Optional[str] = None,
        client_tier: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List companies with optional filtering"""
        try:
            filters = {}
            if sector:
                filters['sector'] = sector
            if client_tier:
                filters['client_tier'] = client_tier
            
            return await self.get_multi(skip=skip, limit=limit, filters=filters)
            
        except Exception as e:
            logger.error(f"❌ BigQuery list_companies failed: {e}")
            return []
    
    async def search_companies(self, search_term: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Search companies by name or description"""
        try:
            # Use BigQuery search capabilities
            query = f"""
            SELECT *
            FROM `{self.table_id}`
            WHERE LOWER(name) LIKE LOWER(@search_term)
               OR LOWER(description) LIKE LOWER(@search_term)
            ORDER BY name
            LIMIT @limit
            """
            
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("search_term", "STRING", f"%{search_term}%"),
                    bigquery.ScalarQueryParameter("limit", "INT64", limit)
                ]
            )
            
            query_job = self.client.query(query, job_config=job_config)
            results = query_job.result()
            
            return [self._convert_from_bq_format(dict(row)) for row in results]
            
        except Exception as e:
            logger.error(f"❌ BigQuery search_companies failed: {e}")
            return []


# Global instance
bigquery_company = BigQueryCompanyCRUD() 