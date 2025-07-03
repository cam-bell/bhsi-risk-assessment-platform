#!/usr/bin/env python3
"""
Orchestrator Factory - Switch between real and mock search orchestrators
"""

import logging
from typing import Union
from app.core.config import settings
from app.agents.search.streamlined_orchestrator import StreamlinedSearchOrchestrator

logger = logging.getLogger(__name__)


def get_search_orchestrator() -> StreamlinedSearchOrchestrator:
    """
    Factory function to get the appropriate search orchestrator
    """
    logger.info("🔍 Using Real Search Orchestrator (USE_MOCK_ORCHESTRATOR=False)")
    return StreamlinedSearchOrchestrator() 