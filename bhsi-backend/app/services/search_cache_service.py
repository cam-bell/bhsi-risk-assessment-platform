#!/usr/bin/env python3
"""
Search Cache Service - Check BigQuery for existing search results before performing new searches
"""

import logging
import hashlib
import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from app.crud.bigquery_events import bigquery_events
from app.crud.bigquery_raw_docs import bigquery_raw_docs
from app.agents.search.orchestrator_factory import get_search_orchestrator
from app.services.bigquery_database_integration import bigquery_db_integration

logger = logging.getLogger(__name__)


def map_risk_level_to_color(risk_level: str) -> str:
    """Map risk level to color (green, orange, red)"""
    if risk_level.startswith("High"):
        return "red"
    elif risk_level.startswith("Medium"):
        return "orange"
    elif risk_level.startswith("Low") or risk_level == "No-Legal":
        return "green"
    else:
        return "gray"  # For Unknown or other cases


class SearchCacheService:
    """Service to cache and retrieve search results from BigQuery"""
    
    def __init__(self):
        self.events_crud = bigquery_events
        self.raw_docs_crud = bigquery_raw_docs
        self.orchestrator = get_search_orchestrator()
        self.db_integration = bigquery_db_integration
    
    def _generate_search_key(
        self, 
        company_name: str, 
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        days_back: Optional[int] = None,
        active_agents: List[str] = None
    ) -> str:
        """Generate a unique key for this search request"""
        search_params = {
            "company_name": company_name.lower().strip(),
            "start_date": start_date,
            "end_date": end_date,
            "days_back": days_back,
            "active_agents": sorted(active_agents or [])
        }
        
        # Create a hash of the search parameters
        search_string = json.dumps(search_params, sort_keys=True)
        return hashlib.sha256(search_string.encode()).hexdigest()
    
    async def get_cached_results(
        self,
        company_name: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        days_back: Optional[int] = None,
        active_agents: List[str] = None,
        cache_age_hours: int = 24
    ) -> Optional[Dict[str, Any]]:
        """
        Check if search results are cached in BigQuery
        
        Args:
            company_name: Company to search for
            start_date: Start date for search
            end_date: End date for search
            days_back: Days back to search
            active_agents: List of active search agents
            cache_age_hours: Maximum age of cached results in hours
            
        Returns:
            Cached results if available and fresh, None otherwise
        """
        try:
            # Ensure numeric types robustly at the very beginning
            logger.debug(f"🔍 Initial days_back type: {type(days_back)}, value: {days_back}")
            if days_back is not None:
                try:
                    days_back = int(days_back)
                    logger.debug(f"✅ Converted days_back to int at start: {days_back}")
                except (ValueError, TypeError) as e:
                    logger.warning(f"⚠️ Failed to convert days_back '{days_back}' to int at start: {e}")
                    days_back = 30  # Safe fallback
            if cache_age_hours is not None:
                try:
                    cache_age_hours = int(cache_age_hours)
                except (ValueError, TypeError):
                    cache_age_hours = 24

            search_key = self._generate_search_key(
                company_name, start_date, end_date, days_back, active_agents
            )
            
            # Calculate cache cutoff time
            cache_cutoff = datetime.utcnow() - timedelta(hours=cache_age_hours)
            
            # Search for events with this company name and recent timestamp
            events = await self.events_crud.search_by_company(
                company_name=company_name,
                limit=1000  # Get all events for this company
            )
            
            if not events:
                logger.info(f"No cached events found for company: {company_name}")
                return None
            
            # Filter events by date range if specified
            filtered_events = []
            for event in events:
                event_date = None
                if event.get('pub_date'):
                    try:
                        if isinstance(event['pub_date'], str):
                            event_date = datetime.fromisoformat(event['pub_date'].replace('Z', '+00:00'))
                        else:
                            event_date = event['pub_date']
                    except:
                        continue
                
                # Check if event is within date range
                if start_date and event_date:
                    try:
                        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
                        # Convert both to date objects for comparison
                        if isinstance(event_date, datetime):
                            event_date_only = event_date.date()
                        else:
                            event_date_only = event_date
                        if isinstance(start_dt, datetime):
                            start_date_only = start_dt.date()
                        else:
                            start_date_only = start_dt
                        if event_date_only < start_date_only:
                            continue
                    except Exception as e:
                        logger.debug(f"Date comparison error for start_date: {e}")
                        pass
                
                if end_date and event_date:
                    try:
                        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
                        # Convert both to date objects for comparison
                        if isinstance(event_date, datetime):
                            event_date_only = event_date.date()
                        else:
                            event_date_only = event_date
                        if isinstance(end_dt, datetime):
                            end_date_only = end_dt.date()
                        else:
                            end_date_only = end_dt
                        if event_date_only > end_date_only:
                            continue
                    except Exception as e:
                        logger.debug(f"Date comparison error for end_date: {e}")
                        pass
                
                # Check if event is within days_back
                if days_back and event_date:
                    # Ensure days_back is an integer
                    try:
                        days_back_int = int(days_back) if days_back is not None else 30
                        logger.debug(f"✅ Using days_back_int: {days_back_int}")
                    except (ValueError, TypeError) as e:
                        logger.warning(f"⚠️ Failed to convert days_back '{days_back}' to int: {e}")
                        days_back_int = 30  # Default fallback
                    
                    cutoff_date = datetime.utcnow() - timedelta(days=days_back_int)
                    # Convert both to date objects for comparison
                    if isinstance(event_date, datetime):
                        event_date_only = event_date.date()
                    else:
                        event_date_only = event_date
                    if isinstance(cutoff_date, datetime):
                        cutoff_date_only = cutoff_date.date()
                    else:
                        cutoff_date_only = cutoff_date
                    if event_date_only < cutoff_date_only:
                        continue
                
                filtered_events.append(event)
            
            # Check if we have recent enough events
            recent_events = [
                event for event in filtered_events
                if event.get('created_at') and 
                datetime.fromisoformat(event['created_at'].replace('Z', '+00:00')) > cache_cutoff
            ]
            
            if not recent_events:
                logger.info(f"No recent cached events found for company: {company_name}")
                return None
            
            # Group events by source
            events_by_source = {}
            for event in filtered_events:
                source = event.get('source', 'Unknown')
                if source not in events_by_source:
                    events_by_source[source] = []
                events_by_source[source].append(event)
            
            # Convert to search results format
            cached_results = {}
            
            # Convert BOE events
            if 'BOE' in events_by_source:
                cached_results['boe'] = {
                    'results': [
                        {
                            'identificador': event.get('event_id', '').split(':')[-1],
                            'titulo': event.get('title', ''),
                            'text': event.get('text', ''),
                            'fechaPublicacion': event.get('pub_date', ''),
                            'url_html': event.get('url', ''),
                            'seccion_codigo': event.get('section', ''),
                            'seccion_nombre': event.get('section', ''),
                            'summary': event.get('text', '')[:200] + '...' if len(event.get('text', '')) > 200 else event.get('text', ''),
                            'risk_level': event.get('risk_label', 'Unknown'),
                            'confidence': event.get('confidence', 0.5),
                            'method': 'cached',
                            'risk_color': map_risk_level_to_color(event.get('risk_label', 'Unknown'))
                        }
                        for event in events_by_source['BOE']
                    ]
                }
            
            # Convert NewsAPI events
            if 'NewsAPI' in events_by_source:
                cached_results['newsapi'] = {
                    'articles': [
                        {
                            'title': event.get('title', ''),
                            'description': event.get('text', '')[:200] + '...' if len(event.get('text', '')) > 200 else event.get('text', ''),
                            'content': event.get('text', ''),
                            'publishedAt': event.get('pub_date', ''),
                            'url': event.get('url', ''),
                            'author': event.get('author', 'Unknown'),
                            'source': {'name': event.get('section', 'NewsAPI')},
                            'risk_level': event.get('risk_label', 'Unknown'),
                            'confidence': event.get('confidence', 0.5),
                            'method': 'cached',
                            'risk_color': map_risk_level_to_color(event.get('risk_label', 'Unknown'))
                        }
                        for event in events_by_source['NewsAPI']
                    ]
                }
            
            # Convert RSS events
            rss_sources = ['RSS-ELPAIS', 'RSS-EXPANSION', 'RSS-ELMUNDO', 'RSS-ABC', 
                          'RSS-LAVANGUARDIA', 'RSS-ELCONFIDENCIAL', 'RSS-ELDIARIO', 'RSS-EUROPAPRESS']
            
            for rss_source in rss_sources:
                if rss_source in events_by_source:
                    source_key = rss_source.lower().replace('rss-', '')
                    cached_results[source_key] = {
                        'articles': [
                            {
                                'title': event.get('title', ''),
                                'description': event.get('text', '')[:200] + '...' if len(event.get('text', '')) > 200 else event.get('text', ''),
                                'content': event.get('text', ''),
                                'publishedAt': event.get('pub_date', ''),
                                'url': event.get('url', ''),
                                'author': event.get('author', 'Unknown'),
                                'source_name': rss_source,
                                'risk_level': event.get('risk_label', 'Unknown'),
                                'confidence': event.get('confidence', 0.5),
                                'method': 'cached',
                                'risk_color': map_risk_level_to_color(event.get('risk_label', 'Unknown'))
                            }
                            for event in events_by_source[rss_source]
                        ]
                    }
            
            if cached_results:
                logger.info(f"✅ Found cached results for {company_name}: {len(filtered_events)} events")
                return {
                    'results': cached_results,
                    'cached': True,
                    'cache_age_hours': cache_age_hours,
                    'total_events': len(filtered_events),
                    'sources': list(cached_results.keys())
                }
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error checking cache for {company_name}: {e}")
            return None
    
    async def perform_search_and_cache(
        self,
        company_name: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        days_back: Optional[int] = None,
        active_agents: List[str] = None
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Perform search and cache results in BigQuery
        
        Returns:
            Tuple of (search_results, db_stats)
        """
        try:
            # Perform the search
            search_results = await self.orchestrator.search_all(
                query=company_name,
                start_date=start_date,
                end_date=end_date,
                days_back=days_back,
                active_agents=active_agents
            )
            
            # Save results to BigQuery
            db_stats = await self.db_integration.save_search_results(
                search_results, company_name, company_name
            )
            
            logger.info(f"✅ Performed new search for {company_name} and cached results")
            
            return search_results, db_stats
            
        except Exception as e:
            logger.error(f"❌ Error performing search for {company_name}: {e}")
            raise
    
    async def get_search_results(
        self,
        company_name: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        days_back: Optional[int] = None,
        active_agents: List[str] = None,
        cache_age_hours: int = 24,
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        """
        Get search results with caching logic
        
        Args:
            company_name: Company to search for
            start_date: Start date for search
            end_date: End date for search
            days_back: Days back to search
            active_agents: List of active search agents
            cache_age_hours: Maximum age of cached results in hours
            force_refresh: Force new search even if cached results exist
            
        Returns:
            Search results with cache metadata
        """
        try:
            # Ensure numeric types
            logger.debug(f"🔍 Initial days_back type: {type(days_back)}, value: {days_back}")
            if days_back is not None:
                try:
                    days_back = int(days_back)
                    logger.debug(f"✅ Converted days_back to int: {days_back}")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to convert days_back '{days_back}' to int: {e}")
                    days_back = 30  # Default fallback
            if cache_age_hours is not None:
                try:
                    cache_age_hours = int(cache_age_hours)
                except Exception:
                    cache_age_hours = 24

            # Check cache first (unless force refresh)
            if not force_refresh:
                cached_results = await self.get_cached_results(
                    company_name, start_date, end_date, days_back, active_agents, cache_age_hours
                )
                
                if cached_results:
                    return {
                        **cached_results,
                        'search_method': 'cached',
                        'cache_info': {
                            'age_hours': cache_age_hours,
                            'total_events': cached_results['total_events'],
                            'sources': cached_results['sources']
                        }
                    }
            
            # Perform new search and cache results
            search_results, db_stats = await self.perform_search_and_cache(
                company_name, start_date, end_date, days_back, active_agents
            )
            
            return {
                'results': search_results,
                'search_method': 'fresh',
                'db_stats': db_stats,
                'cache_info': {
                    'age_hours': 0,
                    'total_events': db_stats.get('events_created', 0),
                    'sources': list(search_results.keys())
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Error in get_search_results for {company_name}: {e}")
            raise


# Global instance
search_cache_service = SearchCacheService() 