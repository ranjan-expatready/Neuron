from sqlalchemy.orm import Session
from typing import Optional, List
from ..models.case import Case
from ..schemas.case import CaseCreate, CaseUpdate
from datetime import datetime
import uuid
import random
import string


class CaseService:
    @staticmethod
    def generate_case_number() -> str:
        """Generate a unique case number"""
        timestamp = datetime.now().strftime("%Y%m%d")
        random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        return f"CA-{timestamp}-{random_suffix}"

    @staticmethod
    def create_case(db: Session, case_data: CaseCreate, org_id: uuid.UUID, created_by: uuid.UUID) -> Case:
        case_number = CaseService.generate_case_number()
        
        # Ensure case number is unique
        while db.query(Case).filter(Case.case_number == case_number).first():
            case_number = CaseService.generate_case_number()

        case = Case(
            org_id=org_id,
            primary_person_id=case_data.primary_person_id,
            case_number=case_number,
            case_type=case_data.case_type,
            title=case_data.title,
            description=case_data.description,
            notes=case_data.notes,
            priority=case_data.priority,
            target_submission_date=case_data.target_submission_date,
            fee_quoted=case_data.fee_quoted,
            metadata=case_data.metadata or {},
            created_by=created_by
        )
        db.add(case)
        db.commit()
        db.refresh(case)
        return case

    @staticmethod
    def get_case_by_id(db: Session, case_id: uuid.UUID, org_id: uuid.UUID) -> Optional[Case]:
        return db.query(Case).filter(
            Case.id == case_id,
            Case.org_id == org_id,
            Case.deleted_at.is_(None)
        ).first()

    @staticmethod
    def get_cases_by_org(db: Session, org_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Case]:
        return db.query(Case).filter(
            Case.org_id == org_id,
            Case.deleted_at.is_(None)
        ).order_by(Case.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def update_case(db: Session, case_id: uuid.UUID, org_id: uuid.UUID, case_data: CaseUpdate) -> Optional[Case]:
        case = CaseService.get_case_by_id(db, case_id, org_id)
        if not case:
            return None

        update_data = case_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(case, field, value)

        case.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(case)
        return case

    @staticmethod
    def delete_case(db: Session, case_id: uuid.UUID, org_id: uuid.UUID) -> bool:
        case = CaseService.get_case_by_id(db, case_id, org_id)
        if not case:
            return False

        case.deleted_at = datetime.utcnow()
        db.commit()
        return True

    @staticmethod
    def get_cases_by_status(db: Session, org_id: uuid.UUID, status: str, skip: int = 0, limit: int = 100) -> List[Case]:
        return db.query(Case).filter(
            Case.org_id == org_id,
            Case.status == status,
            Case.deleted_at.is_(None)
        ).order_by(Case.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_cases_by_type(db: Session, org_id: uuid.UUID, case_type: str, skip: int = 0, limit: int = 100) -> List[Case]:
        return db.query(Case).filter(
            Case.org_id == org_id,
            Case.case_type == case_type,
            Case.deleted_at.is_(None)
        ).order_by(Case.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_cases_by_person(db: Session, org_id: uuid.UUID, person_id: uuid.UUID) -> List[Case]:
        return db.query(Case).filter(
            Case.org_id == org_id,
            Case.primary_person_id == person_id,
            Case.deleted_at.is_(None)
        ).order_by(Case.created_at.desc()).all()