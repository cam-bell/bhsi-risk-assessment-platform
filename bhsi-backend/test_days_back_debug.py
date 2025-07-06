#!/usr/bin/env python3
"""
Debug script to test days_back type conversion
"""

import asyncio
import logging
from datetime import datetime, timedelta

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_days_back_conversion():
    """Test the days_back conversion logic"""
    
    # Test cases
    test_cases = [
        ('7', 'string'),
        (7, 'integer'),
        (None, 'none'),
        ('30', 'string'),
        (30, 'integer'),
    ]
    
    for days_back, case_type in test_cases:
        logger.info(f"Testing case: {case_type} - {days_back} (type: {type(days_back)})")
        
        try:
            # Simulate the conversion logic from search_cache_service
            if days_back is not None:
                try:
                    days_back_int = int(days_back)
                    logger.info(f"✅ Converted to int: {days_back_int}")
                    
                    # Test timedelta usage
                    cutoff_date = datetime.utcnow() - timedelta(days=days_back_int)
                    logger.info(f"✅ Timedelta works: {cutoff_date}")
                    
                except Exception as e:
                    logger.error(f"❌ Failed to convert '{days_back}' to int: {e}")
                    days_back_int = 30  # Default fallback
                    cutoff_date = datetime.utcnow() - timedelta(days=days_back_int)
                    logger.info(f"✅ Used fallback: {cutoff_date}")
            else:
                logger.info("days_back is None, skipping conversion")
                
        except Exception as e:
            logger.error(f"❌ Error in case {case_type}: {e}")

if __name__ == "__main__":
    test_days_back_conversion() 