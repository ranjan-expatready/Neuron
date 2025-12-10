from __future__ import annotations

from typing import Any, List, Optional

from sqlalchemy.orm import Session

from src.app.config.intake_config import (
    DocumentDefinition,
    FieldDefinition,
    FormDefinition,
    IntakeTemplate,
)
from src.app.config.options_config import load_options_config
from src.app.models.intake_config_draft import IntakeConfigDraft
from src.app.schemas.intake_config_draft import IntakeConfigDraftCreate, IntakeConfigDraftUpdate


class IntakeConfigDraftService:
    def __init__(self, db: Session):
        self.db = db

    def list_drafts(
        self,
        config_type: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[IntakeConfigDraft]:
        query = self.db.query(IntakeConfigDraft)
        if config_type:
            query = query.filter(IntakeConfigDraft.config_type == config_type)
        if status:
            query = query.filter(IntakeConfigDraft.status == status)
        return query.order_by(IntakeConfigDraft.updated_at.desc()).all()

    def get(self, draft_id: str) -> Optional[IntakeConfigDraft]:
        return self.db.query(IntakeConfigDraft).filter(IntakeConfigDraft.id == draft_id).first()

    def create(self, payload: IntakeConfigDraftCreate, user_id: str) -> IntakeConfigDraft:
        self._validate_payload(payload.config_type, payload.payload)
        draft = IntakeConfigDraft(
            config_type=payload.config_type,
            key=payload.key,
            status=payload.status,
            payload=payload.payload,
            notes=payload.notes,
            created_by=user_id,
            updated_by=user_id,
        )
        self.db.add(draft)
        self.db.commit()
        self.db.refresh(draft)
        return draft

    def update(self, draft_id: str, payload: IntakeConfigDraftUpdate, user_id: str) -> IntakeConfigDraft:
        draft = self.get(draft_id)
        if not draft:
            raise ValueError("Draft not found")
        new_payload = payload.payload if payload.payload is not None else draft.payload
        if payload.payload is not None:
            self._validate_payload(draft.config_type, payload.payload)
        draft.key = payload.key or draft.key
        draft.payload = new_payload
        if payload.status:
            draft.status = payload.status
        if payload.notes is not None:
            draft.notes = payload.notes
        draft.updated_by = user_id
        self.db.commit()
        self.db.refresh(draft)
        return draft

    def delete(self, draft_id: str, user_id: str) -> None:
        draft = self.get(draft_id)
        if not draft:
            return
        draft.status = "rejected"
        draft.updated_by = user_id
        self.db.commit()

    def _validate_payload(self, config_type: str, payload: dict[str, Any]) -> None:
        """
        Lightweight validation using existing Pydantic models. This does not activate config.
        """
        if config_type == "field":
            FieldDefinition(**payload)
        elif config_type == "template":
            IntakeTemplate(**payload)
        elif config_type == "document":
            DocumentDefinition(**payload)
        elif config_type == "form":
            FormDefinition(**payload)
        else:
            raise ValueError("Invalid config_type")
        # Optionally ensure options_ref exists
        if config_type == "field" and payload.get("options_ref"):
            bundle = load_options_config()
            ref = payload["options_ref"]
            if isinstance(ref, str) and ref not in bundle.options:
                raise ValueError(f"options_ref '{ref}' is not defined in options.yaml")

