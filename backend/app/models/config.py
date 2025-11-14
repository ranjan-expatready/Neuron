from sqlalchemy import Column, String, DateTime, Boolean, Integer, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from ..db.database import Base


class ConfigCaseType(Base):
    __tablename__ = "config_case_types"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    code = Column(String(100), unique=True, nullable=False, index=True)  # EXPRESS_ENTRY_FSW, STUDY_PERMIT
    name = Column(String(255), nullable=False)
    description = Column(Text)
    category = Column(String(100))  # immigration, study, work, family
    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)
    config_metadata = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    forms = relationship("ConfigForm", back_populates="case_type")
    fields = relationship("ConfigField", back_populates="case_type")

    def __repr__(self):
        return f"<ConfigCaseType(code={self.code}, name={self.name})>"


class ConfigForm(Base):
    __tablename__ = "config_forms"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    case_type_id = Column(String(36), ForeignKey("config_case_types.id", ondelete="CASCADE"), nullable=False)
    code = Column(String(100), nullable=False, index=True)  # personal_info, education, work_experience
    name = Column(String(255), nullable=False)
    description = Column(Text)
    step_number = Column(Integer, default=1)
    is_required = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    form_schema = Column(JSON, default={})  # JSON schema for form validation
    ui_schema = Column(JSON, default={})  # UI rendering configuration
    validation_rules = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    case_type = relationship("ConfigCaseType", back_populates="forms")

    def __repr__(self):
        return f"<ConfigForm(code={self.code}, name={self.name})>"


class ConfigField(Base):
    __tablename__ = "config_fields"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    case_type_id = Column(String(36), ForeignKey("config_case_types.id", ondelete="CASCADE"), nullable=False)
    form_code = Column(String(100), nullable=False)  # links to ConfigForm.code
    field_code = Column(String(100), nullable=False, index=True)
    field_name = Column(String(255), nullable=False)
    field_type = Column(String(50), nullable=False)  # text, number, date, select, checkbox, etc.
    is_required = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)
    validation_rules = Column(JSON, default={})
    options = Column(JSON, default={})  # for select fields, etc.
    help_text = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    case_type = relationship("ConfigCaseType", back_populates="fields")

    def __repr__(self):
        return f"<ConfigField(field_code={self.field_code}, field_name={self.field_name})>"


class ConfigChecklist(Base):
    __tablename__ = "config_checklists"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    case_type_code = Column(String(100), nullable=False, index=True)
    item_code = Column(String(100), nullable=False, index=True)
    item_name = Column(String(255), nullable=False)
    description = Column(Text)
    category = Column(String(100))  # documents, forms, payments, etc.
    is_required = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)
    conditions = Column(JSON, default={})  # conditional logic
    checklist_metadata = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<ConfigChecklist(item_code={self.item_code}, item_name={self.item_name})>"


class ConfigTemplate(Base):
    __tablename__ = "config_templates"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    template_type = Column(String(100), nullable=False, index=True)  # email, document, form
    template_code = Column(String(100), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    subject = Column(String(500))  # for email templates
    content = Column(Text, nullable=False)
    variables = Column(JSON, default={})  # available template variables
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<ConfigTemplate(template_code={self.template_code}, name={self.name})>"


class ConfigFeatureFlag(Base):
    __tablename__ = "config_feature_flags"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    flag_key = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    is_enabled = Column(Boolean, default=False)
    rollout_percentage = Column(Integer, default=0)  # 0-100
    target_orgs = Column(JSON, default=[])  # specific org IDs
    target_users = Column(JSON, default=[])  # specific user IDs
    conditions = Column(JSON, default={})  # additional conditions
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<ConfigFeatureFlag(flag_key={self.flag_key}, is_enabled={self.is_enabled})>"