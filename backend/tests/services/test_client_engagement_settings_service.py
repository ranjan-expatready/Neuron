from src.app.services.client_engagement_settings_service import ClientEngagementSettingsService


def test_settings_default_created(client):
    svc = ClientEngagementSettingsService(client.db_session)
    settings = svc.get_settings_for_tenant(client.default_tenant.id)
    assert settings.auto_intake_reminders_enabled is False
    assert settings.min_days_between_intake_reminders == 7


def test_settings_update(client):
    svc = ClientEngagementSettingsService(client.db_session)
    updated = svc.update_settings(
        client.default_tenant.id,
        auto_intake_reminders_enabled=True,
        min_days_between_intake_reminders=3,
    )
    assert updated.auto_intake_reminders_enabled is True
    assert updated.min_days_between_intake_reminders == 3

