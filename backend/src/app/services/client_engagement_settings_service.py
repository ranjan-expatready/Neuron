from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from src.app.models.client_engagement_settings import ClientEngagementSettings


class ClientEngagementSettingsService:
    def __init__(self, db: Session):
        self.db = db

    def get_settings_for_tenant(self, tenant_id: str) -> ClientEngagementSettings:
        settings = (
            self.db.query(ClientEngagementSettings)
            .filter(ClientEngagementSettings.tenant_id == tenant_id)
            .first()
        )
        if not settings:
            settings = ClientEngagementSettings(tenant_id=tenant_id)
            self.db.add(settings)
            self.db.commit()
            self.db.refresh(settings)
        return settings

    def update_settings(
        self,
        tenant_id: str,
        *,
        auto_intake_reminders_enabled: Optional[bool] = None,
        auto_missing_docs_reminders_enabled: Optional[bool] = None,
        min_days_between_intake_reminders: Optional[int] = None,
        min_days_between_docs_reminders: Optional[int] = None,
    ) -> ClientEngagementSettings:
        settings = self.get_settings_for_tenant(tenant_id)
        if auto_intake_reminders_enabled is not None:
            settings.auto_intake_reminders_enabled = auto_intake_reminders_enabled
        if auto_missing_docs_reminders_enabled is not None:
            settings.auto_missing_docs_reminders_enabled = auto_missing_docs_reminders_enabled
        if min_days_between_intake_reminders is not None:
            settings.min_days_between_intake_reminders = min_days_between_intake_reminders
        if min_days_between_docs_reminders is not None:
            settings.min_days_between_docs_reminders = min_days_between_docs_reminders
        self.db.commit()
        self.db.refresh(settings)
        return settings

