import random
import string
import uuid
from datetime import datetime
from typing import Any, Optional

from sqlalchemy.orm import Session

from ..models.case import Case
from ..schemas.case import CaseCreate, CaseUpdate
from .task import CaseTaskService


class CaseService:
    # Valid case statuses and their allowed transitions
    VALID_STATUSES = ["draft", "active", "submitted", "approved", "rejected", "closed"]
    STATUS_TRANSITIONS = {
        "draft": ["active", "closed"],
        "active": ["submitted", "closed"],
        "submitted": ["approved", "rejected", "active"],
        "approved": ["closed"],
        "rejected": ["active", "closed"],
        "closed": [],  # Terminal state
    }

    @staticmethod
    def generate_case_number() -> str:
        """Generate a unique case number"""
        timestamp = datetime.now().strftime("%Y%m%d")
        random_suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
        return f"CA-{timestamp}-{random_suffix}"

    @staticmethod
    def can_transition_status(current_status: str, new_status: str) -> bool:
        """Check if status transition is allowed"""
        if current_status not in CaseService.STATUS_TRANSITIONS:
            return False
        return new_status in CaseService.STATUS_TRANSITIONS[current_status]

    @staticmethod
    def create_case(db: Session, case_data: CaseCreate, org_id: str, created_by: str) -> Case:
        """Create a new case with lifecycle management"""
        case_number = CaseService.generate_case_number()

        # Ensure case number is unique
        while db.query(Case).filter(Case.case_number == case_number).first():
            case_number = CaseService.generate_case_number()

        case = Case(
            id=str(uuid.uuid4()),
            org_id=org_id,
            primary_person_id=str(case_data.primary_person_id),
            case_number=case_number,
            case_type=case_data.case_type,
            title=case_data.title,
            description=case_data.description,
            notes=case_data.notes,
            priority=case_data.priority or "normal",
            status="draft",  # Always start as draft
            target_submission_date=case_data.target_submission_date,
            fee_quoted=case_data.fee_quoted,
            case_metadata=case_data.metadata or {},
            created_by=created_by,
        )
        db.add(case)
        db.commit()
        db.refresh(case)

        # Bootstrap workflow tasks (best-effort, won't fail case creation)
        try:
            CaseTaskService.bootstrap_case_tasks(db, case)
        except Exception:
            # Do not block case creation due to task bootstrap failure
            pass

        return case

    @staticmethod
    def get_case_by_id(db: Session, case_id: str, org_id: str) -> Optional[Case]:
        """Get a case by ID with multi-tenant isolation"""
        return (
            db.query(Case)
            .filter(Case.id == case_id, Case.org_id == org_id, Case.deleted_at.is_(None))
            .first()
        )

    @staticmethod
    def get_cases_by_org(db: Session, org_id: str, skip: int = 0, limit: int = 100) -> list[Case]:
        """Get all cases for an organization with pagination"""
        return (
            db.query(Case)
            .filter(Case.org_id == org_id, Case.deleted_at.is_(None))
            .order_by(Case.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def update_case(
        db: Session, case_id: str, org_id: str, case_data: CaseUpdate
    ) -> Optional[Case]:
        """Update a case with lifecycle management"""
        case = CaseService.get_case_by_id(db, case_id, org_id)
        if not case:
            return None

        update_data = case_data.model_dump(exclude_unset=True)

        # Map metadata payload to stored column
        if "metadata" in update_data:
            case.case_metadata = update_data.pop("metadata") or {}

        # Handle status transitions with validation
        if "status" in update_data:
            new_status = update_data["status"]
            if new_status not in CaseService.VALID_STATUSES:
                raise ValueError(f"Invalid status: {new_status}")
            if not CaseService.can_transition_status(case.status, new_status):
                raise ValueError(
                    f"Cannot transition from {case.status} to {new_status}. "
                    f"Allowed transitions: {CaseService.STATUS_TRANSITIONS.get(case.status, [])}"
                )

            # Set submitted_at when transitioning to submitted
            if new_status == "submitted" and not case.submitted_at:
                case.submitted_at = datetime.utcnow()

            # Set decision_date when transitioning to approved/rejected
            if new_status in ["approved", "rejected"] and not case.decision_date:
                case.decision_date = datetime.utcnow()

        # Update fields
        for field, value in update_data.items():
            if hasattr(case, field):
                setattr(case, field, value)

        case.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(case)
        return case

    @staticmethod
    def delete_case(db: Session, case_id: str, org_id: str) -> bool:
        """Soft delete a case (multi-tenant safe)"""
        case = CaseService.get_case_by_id(db, case_id, org_id)
        if not case:
            return False

        case.deleted_at = datetime.utcnow()
        db.commit()
        return True

    @staticmethod
    def get_cases_by_status(
        db: Session, org_id: str, status: str, skip: int = 0, limit: int = 100
    ) -> list[Case]:
        """Get cases by status with multi-tenant isolation"""
        if status not in CaseService.VALID_STATUSES:
            raise ValueError(f"Invalid status: {status}")

        return (
            db.query(Case)
            .filter(Case.org_id == org_id, Case.status == status, Case.deleted_at.is_(None))
            .order_by(Case.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_cases_by_type(
        db: Session, org_id: str, case_type: str, skip: int = 0, limit: int = 100
    ) -> list[Case]:
        """Get cases by type with multi-tenant isolation"""
        return (
            db.query(Case)
            .filter(Case.org_id == org_id, Case.case_type == case_type, Case.deleted_at.is_(None))
            .order_by(Case.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_cases_by_person(db: Session, org_id: str, person_id: str) -> list[Case]:
        """Get all cases for a person with multi-tenant isolation"""
        return (
            db.query(Case)
            .filter(
                Case.org_id == org_id,
                Case.primary_person_id == person_id,
                Case.deleted_at.is_(None),
            )
            .order_by(Case.created_at.desc())
            .all()
        )

    @staticmethod
    def get_cases_by_assigned_user(
        db: Session, org_id: str, user_id: str, skip: int = 0, limit: int = 100
    ) -> list[Case]:
        """Get cases assigned to a specific user"""
        return (
            db.query(Case)
            .filter(Case.org_id == org_id, Case.assigned_to == user_id, Case.deleted_at.is_(None))
            .order_by(Case.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_case_statistics(db: Session, org_id: str) -> dict[str, Any]:
        """Get case statistics for an organization"""
        total = db.query(Case).filter(Case.org_id == org_id, Case.deleted_at.is_(None)).count()

        stats = {"total": total}
        for status in CaseService.VALID_STATUSES:
            count = (
                db.query(Case)
                .filter(Case.org_id == org_id, Case.status == status, Case.deleted_at.is_(None))
                .count()
            )
            stats[status] = count

        return stats
