"""
Seed a deterministic user + organization for TestSprite automation.

Usage:
    cd backend && source venv/bin/activate
    python scripts/seed_testsprite_user.py

Outputs a JSON blob with the seeded credentials and freshly minted JWT token.
"""
import json
import os
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from app.db.database import SessionLocal
from app.models.organization import Organization, OrganizationMembership
from app.models.user import User
from app.services.auth import AuthService

load_dotenv()

DEFAULT_EMAIL = os.getenv("TESTSPRITE_USER_EMAIL", "testsprite.automation@canadaos.dev")
DEFAULT_PASSWORD = os.getenv("TESTSPRITE_USER_PASSWORD", "TestSprite!234")
DEFAULT_FIRST_NAME = os.getenv("TESTSPRITE_USER_FIRST_NAME", "TestSprite")
DEFAULT_LAST_NAME = os.getenv("TESTSPRITE_USER_LAST_NAME", "Automation")
DEFAULT_ORG_NAME = os.getenv("TESTSPRITE_ORG_NAME", "TestSprite Automation Org")
DEFAULT_ORG_DOMAIN = os.getenv("TESTSPRITE_ORG_DOMAIN", "testsprite-automation.local")


def seed_user(session):
    user = session.query(User).filter(User.email == DEFAULT_EMAIL).first()
    created = False

    if not user:
        hashed_password = AuthService.get_password_hash(DEFAULT_PASSWORD)
        user = User(
            email=DEFAULT_EMAIL,
            encrypted_password=hashed_password,
            first_name=DEFAULT_FIRST_NAME,
            last_name=DEFAULT_LAST_NAME,
            profile={"source": "testsprite_seed"},
        )
        session.add(user)
        session.flush()
        created = True

    return user, created


def seed_org(session):
    org = session.query(Organization).filter(Organization.name == DEFAULT_ORG_NAME).first()
    created = False

    if not org:
        org = Organization(
            name=DEFAULT_ORG_NAME,
            domain=DEFAULT_ORG_DOMAIN,
            type="automation_lab",
            settings={"seeded_by": "testsprite_script"},
        )
        session.add(org)
        session.flush()
        created = True

    return org, created


def seed_membership(session, user, org):
    membership = (
        session.query(OrganizationMembership)
        .filter(
            OrganizationMembership.user_id == user.id,
            OrganizationMembership.org_id == org.id,
        )
        .first()
    )

    if not membership:
        membership = OrganizationMembership(
            user_id=user.id,
            org_id=org.id,
            role="admin",
            status="active",
        )
        session.add(membership)
        session.flush()


def main():
    session = SessionLocal()
    try:
        user, user_created = seed_user(session)
        org, org_created = seed_org(session)
        seed_membership(session, user, org)
        session.commit()

        token = AuthService.create_access_token({"sub": user.email})

        output = {
            "testsprite_user": {
                "email": user.email,
                "password": DEFAULT_PASSWORD,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "organization": org.name,
            },
            "created_at": datetime.utcnow().isoformat(),
            "user_created": user_created,
            "organization_created": org_created,
            "instructions": "Paste the JWT token into TestSprite's Bearer Token field.",
            "jwt_token": token,
        }

        print(json.dumps(output, indent=2))
    finally:
        session.close()


if __name__ == "__main__":
    main()
