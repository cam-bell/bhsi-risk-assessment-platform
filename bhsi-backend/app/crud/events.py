from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, date

from app.models.events import Event, RiskLabel


class CRUDEvent:
    def create_from_raw(
        self,
        db: Session,
        *,
        raw_id: str,
        source: str,
        title: str,
        text: str,
        section: Optional[str] = None,
        pub_date: Optional[date] = None,
        url: Optional[str] = None
    ) -> Event:
        """Create event from raw document data"""
        event_id = f"{source}:{raw_id}"
        
        # Check if already exists
        existing = db.query(Event).filter(Event.event_id == event_id).first()
        if existing:
            return existing
        
        db_obj = Event(
            event_id=event_id,
            title=title,
            text=text,
            source=source,
            section=section,
            pub_date=pub_date,
            url=url
        )
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_unembedded(self, db: Session, limit: int = 100) -> List[Event]:
        """Get events that need embedding (embedding IS NULL)"""
        return (
            db.query(Event)
            .filter(Event.embedding.is_(None))
            .limit(limit)
            .all()
        )

    def mark_embedded(
        self, 
        db: Session, 
        event_id: str, 
        embedding_model: str = "paraphrase-multilingual-MiniLM-L12-v2"
    ) -> bool:
        """Mark event as embedded"""
        db_obj = db.query(Event).filter(Event.event_id == event_id).first()
        if db_obj:
            db_obj.embedding = "vectorised"
            db_obj.embedding_model = embedding_model
            db_obj.updated_at = datetime.utcnow()
            db.commit()
            return True
        return False

    def get_unclassified(self, db: Session, limit: int = 100) -> List[Event]:
        """Get events that need risk classification (risk_label IS NULL)"""
        return (
            db.query(Event)
            .filter(Event.risk_label.is_(None))
            .limit(limit)
            .all()
        )

    def update_classification(
        self,
        db: Session,
        event_id: str,
        risk_label: str,
        rationale: str,
        confidence: float
    ) -> bool:
        """Update risk classification for event"""
        db_obj = db.query(Event).filter(Event.event_id == event_id).first()
        if db_obj:
            db_obj.risk_label = risk_label
            db_obj.rationale = rationale
            db_obj.confidence = confidence
            db_obj.classifier_ts = datetime.utcnow()
            db_obj.updated_at = datetime.utcnow()
            db.commit()
            return True
        return False

    def get_high_risk(self, db: Session, days_back: int = 7) -> List[Event]:
        """Get high-risk events for notifications"""
        cutoff_date = datetime.utcnow().date()
        from datetime import timedelta
        cutoff_date = cutoff_date - timedelta(days=days_back)
        
        return (
            db.query(Event)
            .filter(Event.risk_label == RiskLabel.HIGH_LEGAL.value)
            .filter(func.date(Event.created_at) >= cutoff_date)
            .order_by(Event.confidence.desc())
            .all()
        )

    def get_risk_summary(self, db: Session, days_back: int = 7) -> Dict[str, Any]:
        """Get risk statistics for recent events"""
        cutoff_date = datetime.utcnow().date()
        from datetime import timedelta
        cutoff_date = cutoff_date - timedelta(days=days_back)
        
        # Count by risk level
        stats = {}
        for risk_level in RiskLabel:
            count = (
                db.query(Event)
                .filter(Event.risk_label == risk_level.value)
                .filter(func.date(Event.created_at) >= cutoff_date)
                .count()
            )
            stats[risk_level.value] = count
        
        # Total events
        stats["total"] = (
            db.query(Event)
            .filter(func.date(Event.created_at) >= cutoff_date)
            .count()
        )
        
        # Processing status
        stats["unembedded"] = db.query(Event).filter(Event.embedding.is_(None)).count()
        stats["unclassified"] = db.query(Event).filter(Event.risk_label.is_(None)).count()
        
        return stats

    def search_by_company(self, db: Session, company_name: str, limit: int = 50) -> List[Event]:
        """Search events mentioning a specific company"""
        return (
            db.query(Event)
            .filter(
                Event.title.ilike(f"%{company_name}%") |
                Event.text.ilike(f"%{company_name}%")
            )
            .order_by(Event.pub_date.desc())
            .limit(limit)
            .all()
        )

    def get_by_section(self, db: Session, section: str, limit: int = 100) -> List[Event]:
        """Get events by BOE section"""
        return (
            db.query(Event)
            .filter(Event.section == section)
            .order_by(Event.pub_date.desc())
            .limit(limit)
            .all()
        )


events = CRUDEvent() 