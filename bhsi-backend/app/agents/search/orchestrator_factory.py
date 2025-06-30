#!/usr/bin/env python3
"""
Orchestrator Factory - Switch between real and mock search orchestrators
"""

import logging
from typing import Union
from app.core.config import settings
from app.agents.search.streamlined_orchestrator import StreamlinedSearchOrchestrator
from app.agents.search.mock_orchestrator import MockSearchOrchestrator

logger = logging.getLogger(__name__)


def get_search_orchestrator() -> Union[StreamlinedSearchOrchestrator, MockSearchOrchestrator]:
    """
    Factory function to get the appropriate search orchestrator
    """
    if settings.USE_MOCK_ORCHESTRATOR:
        logger.info("🎭 Using Mock Search Orchestrator (USE_MOCK_ORCHESTRATOR=True)")
        return MockSearchOrchestrator()
    else:
        logger.info("🔍 Using Real Search Orchestrator (USE_MOCK_ORCHESTRATOR=False)")
        return StreamlinedSearchOrchestrator() 