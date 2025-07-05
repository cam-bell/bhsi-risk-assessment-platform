#!/usr/bin/env python3
"""
BigQuery Schema Definitions for BHSI D&O Risk Assessment System
Defines table schemas for efficient data storage and analytics
"""

from google.cloud import bigquery
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class BigQuerySchemaManager:
    """Manages BigQuery table schemas and creation"""
    
    def __init__(self, project_id: str, dataset_id: str):
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.client = bigquery.Client(project=project_id)
        
    def get_companies_table_schema(self) -> List[bigquery.SchemaField]:
        """Schema for companies table - master company data"""
        return [
            bigquery.SchemaField("vat", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("company_name", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("sector", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("industry", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("client_tier", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("country", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("region", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("employee_count", "INTEGER", mode="NULLABLE"),
            bigquery.SchemaField("revenue_range", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("updated_at", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("last_assessment_date", "TIMESTAMP", mode="NULLABLE"),
            bigquery.SchemaField("total_assessments", "INTEGER", mode="NULLABLE"),
            bigquery.SchemaField("overall_risk_level", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("risk_score", "FLOAT64", mode="NULLABLE"),
        ]
    
    def get_assessments_table_schema(self) -> List[bigquery.SchemaField]:
        """Schema for assessments table - risk assessment results"""
        return [
            bigquery.SchemaField("assessment_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("company_vat", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("user_id", "STRING", mode="REQUIRED"),
            
            # Risk scores (green/orange/red)
            bigquery.SchemaField("turnover_risk", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("shareholding_risk", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("bankruptcy_risk", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("legal_risk", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("corruption_risk", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("overall_risk", "STRING", mode="REQUIRED"),
            
            # Financial metrics
            bigquery.SchemaField("financial_score", "FLOAT64", mode="NULLABLE"),
            bigquery.SchemaField("legal_score", "FLOAT64", mode="NULLABLE"),
            bigquery.SchemaField("press_score", "FLOAT64", mode="NULLABLE"),
            bigquery.SchemaField("composite_score", "FLOAT64", mode="NULLABLE"),
            
            # Search metadata
            bigquery.SchemaField("search_date_range_start", "DATE", mode="NULLABLE"),
            bigquery.SchemaField("search_date_range_end", "DATE", mode="NULLABLE"),
            bigquery.SchemaField("sources_searched", "STRING", mode="NULLABLE"),  # JSON array
            bigquery.SchemaField("total_results_found", "INTEGER", mode="NULLABLE"),
            bigquery.SchemaField("high_risk_results", "INTEGER", mode="NULLABLE"),
            bigquery.SchemaField("medium_risk_results", "INTEGER", mode="NULLABLE"),
            bigquery.SchemaField("low_risk_results", "INTEGER", mode="NULLABLE"),
            
            # Analysis metadata
            bigquery.SchemaField("analysis_summary", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("key_findings", "STRING", mode="NULLABLE"),  # JSON array
            bigquery.SchemaField("recommendations", "STRING", mode="NULLABLE"),  # JSON array
            bigquery.SchemaField("classification_method", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("processing_time_seconds", "FLOAT64", mode="NULLABLE"),
            
            # Timestamps
            bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("updated_at", "TIMESTAMP", mode="REQUIRED"),
        ]
    
    def get_events_table_schema(self) -> List[bigquery.SchemaField]:
        """Schema for events table - normalized risk events"""
        return [
            bigquery.SchemaField("event_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("company_vat", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("company_name", "STRING", mode="NULLABLE"),
            
            # Event content
            bigquery.SchemaField("title", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("text", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("summary", "STRING", mode="NULLABLE"),
            
            # Source information
            bigquery.SchemaField("source", "STRING", mode="REQUIRED"),  # BOE, NewsAPI, RSS, etc.
            bigquery.SchemaField("source_name", "STRING", mode="NULLABLE"),  # Specific source name
            bigquery.SchemaField("section", "STRING", mode="NULLABLE"),  # BOE section, news category
            bigquery.SchemaField("url", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("author", "STRING", mode="NULLABLE"),
            
            # Risk classification
            bigquery.SchemaField("risk_level", "STRING", mode="REQUIRED"),  # High-Legal, Medium-Legal, etc.
            bigquery.SchemaField("risk_category", "STRING", mode="NULLABLE"),  # Legal, Financial, Regulatory
            bigquery.SchemaField("confidence", "FLOAT64", mode="NULLABLE"),
            bigquery.SchemaField("classification_method", "STRING", mode="NULLABLE"),  # keyword_gate, llm, etc.
            bigquery.SchemaField("rationale", "STRING", mode="NULLABLE"),
            
            # Dates
            bigquery.SchemaField("event_date", "DATE", mode="NULLABLE"),
            bigquery.SchemaField("publication_date", "DATE", mode="NULLABLE"),
            bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("updated_at", "TIMESTAMP", mode="REQUIRED"),
            
            # Processing metadata
            bigquery.SchemaField("processing_time_ms", "FLOAT64", mode="NULLABLE"),
            bigquery.SchemaField("embedding_status", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("embedding_model", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("alerted", "BOOLEAN", mode="NULLABLE"),
        ]
    
    def get_raw_docs_table_schema(self) -> List[bigquery.SchemaField]:
        """Schema for raw_docs table - original scraped documents"""
        return [
            bigquery.SchemaField("doc_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("source", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("source_name", "STRING", mode="NULLABLE"),
            
            # Original payload
            bigquery.SchemaField("raw_payload", "STRING", mode="REQUIRED"),  # JSON string
            bigquery.SchemaField("document_type", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("identificador", "STRING", mode="NULLABLE"),  # BOE identifier
            
            # Metadata
            bigquery.SchemaField("title", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("url", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("publication_date", "DATE", mode="NULLABLE"),
            bigquery.SchemaField("section", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("author", "STRING", mode="NULLABLE"),
            
            # Processing status
            bigquery.SchemaField("processing_status", "STRING", mode="REQUIRED"),  # pending, processed, failed
            bigquery.SchemaField("processing_attempts", "INTEGER", mode="NULLABLE"),
            bigquery.SchemaField("error_message", "STRING", mode="NULLABLE"),
            
            # Timestamps
            bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("updated_at", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("processed_at", "TIMESTAMP", mode="NULLABLE"),
        ]
    
    def get_financial_metrics_table_schema(self) -> List[bigquery.SchemaField]:
        """Schema for financial_metrics table - company financial data"""
        return [
            bigquery.SchemaField("metric_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("company_vat", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("source", "STRING", mode="REQUIRED"),  # Yahoo Finance, BORME, etc.
            
            # Financial metrics
            bigquery.SchemaField("metric_date", "DATE", mode="REQUIRED"),
            bigquery.SchemaField("revenue", "FLOAT64", mode="NULLABLE"),
            bigquery.SchemaField("net_income", "FLOAT64", mode="NULLABLE"),
            bigquery.SchemaField("total_assets", "FLOAT64", mode="NULLABLE"),
            bigquery.SchemaField("total_liabilities", "FLOAT64", mode="NULLABLE"),
            bigquery.SchemaField("cash_flow", "FLOAT64", mode="NULLABLE"),
            bigquery.SchemaField("debt_ratio", "FLOAT64", mode="NULLABLE"),
            bigquery.SchemaField("profit_margin", "FLOAT64", mode="NULLABLE"),
            bigquery.SchemaField("current_ratio", "FLOAT64", mode="NULLABLE"),
            bigquery.SchemaField("quick_ratio", "FLOAT64", mode="NULLABLE"),
            
            # Market metrics
            bigquery.SchemaField("market_cap", "FLOAT64", mode="NULLABLE"),
            bigquery.SchemaField("stock_price", "FLOAT64", mode="NULLABLE"),
            bigquery.SchemaField("pe_ratio", "FLOAT64", mode="NULLABLE"),
            bigquery.SchemaField("dividend_yield", "FLOAT64", mode="NULLABLE"),
            
            # Timestamps
            bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("updated_at", "TIMESTAMP", mode="REQUIRED"),
        ]
    
    def get_users_table_schema(self) -> List[bigquery.SchemaField]:
        """Schema for users table - user authentication and authorization"""
        return [
            bigquery.SchemaField("user_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("email", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("first_name", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("last_name", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("hashed_password", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("user_type", "STRING", mode="REQUIRED"),  # "admin" or "user"
            bigquery.SchemaField("is_active", "BOOLEAN", mode="REQUIRED"),
            bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("updated_at", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("last_login", "TIMESTAMP", mode="NULLABLE"),
        ]
    
    def create_tables_if_not_exist(self) -> Dict[str, bool]:
        """Create all tables if they don't exist"""
        tables = {
            "companies": self.get_companies_table_schema(),
            "assessments": self.get_assessments_table_schema(),
            "events": self.get_events_table_schema(),
            "raw_docs": self.get_raw_docs_table_schema(),
            "financial_metrics": self.get_financial_metrics_table_schema(),
            "users": self.get_users_table_schema(),
        }
        
        results = {}
        
        for table_name, schema in tables.items():
            try:
                table_id = f"{self.project_id}.{self.dataset_id}.{table_name}"
                table = bigquery.Table(table_id, schema=schema)
                
                # Set clustering for better query performance
                if table_name == "events":
                    table.clustering_fields = ["company_vat", "risk_level", "publication_date"]
                elif table_name == "assessments":
                    table.clustering_fields = ["company_vat", "created_at"]
                elif table_name == "raw_docs":
                    table.clustering_fields = ["source", "processing_status", "created_at"]
                
                # Create table if it doesn't exist
                table = self.client.create_table(table, exists_ok=True)
                
                # For existing users table, try to disable streaming if possible
                if table_name == "users":
                    try:
                        # Note: BigQuery doesn't allow disabling streaming on existing tables
                        # We'll need to handle this in the update logic
                        logger.info(f"ℹ️ Users table created - streaming buffer limitations apply")
                    except Exception as e:
                        logger.warning(f"Could not configure streaming for {table_name}: {e}")
                
                results[table_name] = True
                logger.info(f"✅ Table {table_name} ready")
                
            except Exception as e:
                logger.error(f"❌ Failed to create table {table_name}: {e}")
                results[table_name] = False
        
        return results
    
    def get_table_reference(self, table_name: str) -> str:
        """Get fully qualified table reference"""
        return f"{self.project_id}.{self.dataset_id}.{table_name}"
    
    def get_schema_for_table(self, table_name: str) -> List[bigquery.SchemaField]:
        """Get schema for a specific table"""
        schemas = {
            "companies": self.get_companies_table_schema(),
            "assessments": self.get_assessments_table_schema(),
            "events": self.get_events_table_schema(),
            "raw_docs": self.get_raw_docs_table_schema(),
            "financial_metrics": self.get_financial_metrics_table_schema(),
            "users": self.get_users_table_schema(),
        }
        return schemas.get(table_name, []) 