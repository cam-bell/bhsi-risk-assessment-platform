"""
Error monitoring and alerting utilities for background tasks
"""
import logging
import time
from typing import Dict, Any, Optional, List
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class ErrorMonitor:
    """Centralized error monitoring for background tasks"""
    
    def __init__(self):
        self.critical_errors: List[Dict[str, Any]] = []
        self.retry_metrics: Dict[str, int] = {}
        self.persistence_metrics: Dict[str, Dict[str, Any]] = {}
    
    def log_critical_error(
        self, 
        operation: str, 
        company_name: str, 
        error: Exception, 
        context: Dict[str, Any] = None
    ) -> None:
        """Log a critical error for alerting"""
        error_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "operation": operation,
            "company_name": company_name,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context or {}
        }
        
        self.critical_errors.append(error_data)
        
        # Log for immediate alerting
        logger.error(
            f"🚨 CRITICAL ERROR: {operation} failed for {company_name}: {error}"
        )
        logger.error(f"📊 Error context: {json.dumps(context or {}, indent=2)}")
        
        # Keep only last 100 critical errors
        if len(self.critical_errors) > 100:
            self.critical_errors = self.critical_errors[-100:]
    
    def track_retry_attempt(self, operation: str) -> None:
        """Track retry attempts for monitoring"""
        self.retry_metrics[operation] = self.retry_metrics.get(operation, 0) + 1
        logger.warning(f"🔄 Retry attempt for {operation}: {self.retry_metrics[operation]}")
    
    def log_persistence_metrics(
        self, 
        company_name: str, 
        metrics: Dict[str, Any]
    ) -> None:
        """Log persistence metrics for monitoring"""
        self.persistence_metrics[company_name] = {
            "timestamp": datetime.utcnow().isoformat(),
            **metrics
        }
        
        # Log structured metrics
        logger.info(f"📊 PERSISTENCE_METRICS for {company_name}: {json.dumps(metrics, indent=2)}")
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get summary of recent errors and metrics"""
        return {
            "critical_errors_count": len(self.critical_errors),
            "recent_critical_errors": self.critical_errors[-10:],  # Last 10
            "retry_metrics": self.retry_metrics,
            "persistence_metrics": self.persistence_metrics
        }
    
    def should_alert(self, operation: str, error_count: int) -> bool:
        """Determine if an alert should be sent based on error patterns"""
        # Alert if more than 5 errors in last hour for same operation
        recent_errors = [
            e for e in self.critical_errors 
            if e["operation"] == operation and 
            (datetime.utcnow() - datetime.fromisoformat(e["timestamp"])).seconds < 3600
        ]
        
        return len(recent_errors) > 5
    
    def generate_alert_message(self, operation: str) -> str:
        """Generate alert message for failed operations"""
        recent_errors = [
            e for e in self.critical_errors 
            if e["operation"] == operation
        ][-5:]  # Last 5 errors
        
        message = f"🚨 ALERT: {operation} has failed {len(recent_errors)} times recently\n"
        message += f"📅 Time: {datetime.utcnow().isoformat()}\n"
        message += f"🔍 Recent errors:\n"
        
        for error in recent_errors:
            message += f"  - {error['company_name']}: {error['error_message']}\n"
        
        return message

# Global error monitor instance
error_monitor = ErrorMonitor()

def log_background_task_error(
    operation: str,
    company_name: str,
    error: Exception,
    context: Dict[str, Any] = None
) -> None:
    """Log background task error for monitoring"""
    error_monitor.log_critical_error(operation, company_name, error, context)
    
    # Check if alert should be sent
    if error_monitor.should_alert(operation, 1):
        alert_message = error_monitor.generate_alert_message(operation)
        logger.critical(f"🚨 BACKGROUND TASK ALERT:\n{alert_message}")

def track_persistence_metrics(
    company_name: str,
    metrics: Dict[str, Any]
) -> None:
    """Track persistence metrics for monitoring"""
    error_monitor.log_persistence_metrics(company_name, metrics)

def get_monitoring_summary() -> Dict[str, Any]:
    """Get monitoring summary for health checks"""
    return error_monitor.get_error_summary() 