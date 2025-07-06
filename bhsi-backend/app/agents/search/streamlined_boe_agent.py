#!/usr/bin/env python3
"""
Streamlined BOE Agent - Fast data fetching only, no classification during search
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from app.agents.search.base_agent import BaseSearchAgent
from app.agents.search.BOE import fetch_boe_summary, iter_items, full_text

logger = logging.getLogger(__name__)


class StreamlinedBOEAgent(BaseSearchAgent):
    """Ultra-fast BOE search - fetches data only, classification happens later"""
    
    def __init__(self):
        super().__init__()
        self.source = "BOE"
    
    async def search(
        self,
        query: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        days_back: Optional[int] = 7
    ) -> Dict[str, Any]:
        """
        FAST BOE search - just fetch and filter, no classification
        """
        try:
            # Determine date range
            today = datetime.now()
            
            if not start_date or not end_date:
                end_date = today.strftime("%Y-%m-%d")
                # Ensure days_back is an integer
                try:
                    days_back_int = int(days_back) if days_back is not None else 7
                except (ValueError, TypeError):
                    days_back_int = 7
                start_date = (today - timedelta(days=days_back_int)).strftime("%Y-%m-%d")
            else:
                # Validate dates
                end_dt = datetime.strptime(end_date, "%Y-%m-%d")
                if end_dt > today:
                    end_date = today.strftime("%Y-%m-%d")
                
                start_dt = datetime.strptime(start_date, "%Y-%m-%d")
                if start_dt > end_dt:
                    start_date, end_date = end_date, start_date
            
            logger.info(f"🔍 BOE search: '{query}' ({start_date} to {end_date})")
            
            results = []
            errors = []
            query_lower = query.lower()
            current_date = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            
            while current_date <= end_dt:
                date_str = current_date.strftime("%Y%m%d")
                try:
                    summary = fetch_boe_summary(date_str)
                    
                    for item in iter_items(summary):
                        try:
                            title = item.get("titulo", "")
                            # Simple string matching - very fast
                            if query_lower in title.lower():
                                # Get full text only if we have a match
                                text = full_text(item)
                                
                                # Create result without classification
                                result = {
                                    "identificador": item.get("identificador", ""),
                                    "titulo": title,
                                    "seccion_codigo": item.get("seccion_codigo", ""),
                                    "seccion_nombre": item.get("seccion_nombre", ""),
                                    "fechaPublicacion": item.get("fecha_publicacion", current_date.strftime("%Y-%m-%d")),
                                    "url_html": item.get("url_html", ""),
                                    "url_xml": item.get("url_xml", ""),
                                    "text": text,
                                    "summary": text[:300] + "..." if len(text) > 300 else text,
                                    "section": item.get("seccion_codigo", "")
                                }
                                results.append(result)
                                logger.debug(f"✅ BOE match: {title[:50]}...")
                                
                        except Exception as e:
                            logger.error(f"Error processing BOE item: {e}")
                            
                except Exception as e:
                    # Expected for non-existent dates
                    if "404" not in str(e):
                        logger.error(f"BOE fetch error {date_str}: {e}")
                        errors.append(f"{date_str}: {e}")
                
                current_date += timedelta(days=1)
            
            logger.info(f"✅ BOE search done: {len(results)} results")
            
            return {
                "search_summary": {
                    "query": query,
                    "date_range": f"{start_date} to {end_date}",
                    "total_results": len(results),
                    "errors": errors[:5]  # Limit error list
                },
                "results": results
            }
            
        except Exception as e:
            logger.error(f"BOE search failed: {e}")
            return {
                "search_summary": {
                    "query": query,
                    "date_range": f"{start_date or 'unknown'} to {end_date or 'unknown'}",
                    "total_results": 0,
                    "errors": [str(e)]
                },
                "results": []
            } 