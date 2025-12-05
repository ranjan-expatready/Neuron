import uuid
from typing import Any, Optional

from sqlalchemy.orm import Session

from ..models.config import (
    ConfigCaseType,
    ConfigChecklist,
    ConfigFeatureFlag,
    ConfigField,
    ConfigForm,
    ConfigTemplate,
)


class ConfigService:
    @staticmethod
    def get_case_types(db: Session, is_active: Optional[bool] = None) -> list[ConfigCaseType]:
        query = db.query(ConfigCaseType)
        if is_active is not None:
            query = query.filter(ConfigCaseType.is_active == is_active)
        return query.order_by(ConfigCaseType.sort_order, ConfigCaseType.name).all()

    @staticmethod
    def get_case_type_by_code(db: Session, code: str) -> Optional[ConfigCaseType]:
        return db.query(ConfigCaseType).filter(ConfigCaseType.code == code).first()

    @staticmethod
    def get_forms_by_case_type(
        db: Session, case_type_code: str, is_active: Optional[bool] = None
    ) -> list[ConfigForm]:
        case_type = ConfigService.get_case_type_by_code(db, case_type_code)
        if not case_type:
            return []

        query = db.query(ConfigForm).filter(ConfigForm.case_type_id == case_type.id)
        if is_active is not None:
            query = query.filter(ConfigForm.is_active == is_active)
        return query.order_by(ConfigForm.step_number, ConfigForm.name).all()

    @staticmethod
    def get_fields_by_case_type(
        db: Session,
        case_type_code: str,
        form_code: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> list[ConfigField]:
        case_type = ConfigService.get_case_type_by_code(db, case_type_code)
        if not case_type:
            return []

        query = db.query(ConfigField).filter(ConfigField.case_type_id == case_type.id)
        if form_code:
            query = query.filter(ConfigField.form_code == form_code)
        if is_active is not None:
            query = query.filter(ConfigField.is_active == is_active)
        return query.order_by(ConfigField.sort_order, ConfigField.field_name).all()

    @staticmethod
    def get_checklist_by_case_type(
        db: Session, case_type_code: str, is_active: Optional[bool] = None
    ) -> list[ConfigChecklist]:
        query = db.query(ConfigChecklist).filter(ConfigChecklist.case_type_code == case_type_code)
        if is_active is not None:
            query = query.filter(ConfigChecklist.is_active == is_active)
        return query.order_by(ConfigChecklist.sort_order, ConfigChecklist.item_name).all()

    @staticmethod
    def get_template_by_code(db: Session, template_code: str) -> Optional[ConfigTemplate]:
        return (
            db.query(ConfigTemplate)
            .filter(ConfigTemplate.template_code == template_code, ConfigTemplate.is_active == True)
            .first()
        )

    @staticmethod
    def get_templates_by_type(db: Session, template_type: str) -> list[ConfigTemplate]:
        return (
            db.query(ConfigTemplate)
            .filter(ConfigTemplate.template_type == template_type, ConfigTemplate.is_active == True)
            .all()
        )

    @staticmethod
    def is_feature_enabled(
        db: Session,
        flag_key: str,
        org_id: Optional[uuid.UUID] = None,
        user_id: Optional[uuid.UUID] = None,
    ) -> bool:
        """Check if a feature flag is enabled for the given context"""
        flag = db.query(ConfigFeatureFlag).filter(ConfigFeatureFlag.flag_key == flag_key).first()
        if not flag:
            return False

        if not flag.is_enabled:
            return False

        # Check specific targeting
        if org_id and flag.target_orgs and str(org_id) not in flag.target_orgs:
            return False

        if user_id and flag.target_users and str(user_id) not in flag.target_users:
            return False

        # Check rollout percentage (simplified - in production you'd want deterministic hashing)
        if flag.rollout_percentage < 100:
            # For now, just return True if rollout > 0
            return flag.rollout_percentage > 0

        return True

    @staticmethod
    def get_case_type_config(db: Session, case_type_code: str) -> dict[str, Any]:
        """Get complete configuration for a case type including forms, fields, and checklist"""
        case_type = ConfigService.get_case_type_by_code(db, case_type_code)
        if not case_type:
            return {}

        forms = ConfigService.get_forms_by_case_type(db, case_type_code, is_active=True)
        fields = ConfigService.get_fields_by_case_type(db, case_type_code, is_active=True)
        checklist = ConfigService.get_checklist_by_case_type(db, case_type_code, is_active=True)

        # Group fields by form
        fields_by_form = {}
        for field in fields:
            if field.form_code not in fields_by_form:
                fields_by_form[field.form_code] = []
            fields_by_form[field.form_code].append(
                {
                    "field_code": field.field_code,
                    "field_name": field.field_name,
                    "field_type": field.field_type,
                    "is_required": field.is_required,
                    "sort_order": field.sort_order,
                    "validation_rules": field.validation_rules,
                    "options": field.options,
                    "help_text": field.help_text,
                }
            )

        return {
            "case_type": {
                "code": case_type.code,
                "name": case_type.name,
                "description": case_type.description,
                "category": case_type.category,
                "metadata": case_type.metadata,
            },
            "forms": [
                {
                    "code": form.code,
                    "name": form.name,
                    "description": form.description,
                    "step_number": form.step_number,
                    "is_required": form.is_required,
                    "form_schema": form.form_schema,
                    "ui_schema": form.ui_schema,
                    "validation_rules": form.validation_rules,
                    "fields": fields_by_form.get(form.code, []),
                }
                for form in forms
            ],
            "checklist": [
                {
                    "item_code": item.item_code,
                    "item_name": item.item_name,
                    "description": item.description,
                    "category": item.category,
                    "is_required": item.is_required,
                    "sort_order": item.sort_order,
                    "conditions": item.conditions,
                }
                for item in checklist
            ],
        }
