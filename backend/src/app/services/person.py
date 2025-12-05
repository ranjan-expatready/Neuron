import uuid
from datetime import datetime
from typing import Optional, Union

from sqlalchemy.orm import Session

from ..models.person import Person
from ..schemas.person import PersonCreate, PersonUpdate


class PersonService:
    @staticmethod
    def create_person(db: Session, person_data: PersonCreate, org_id: str) -> Person:
        person = Person(
            org_id=org_id,
            first_name=person_data.first_name,
            last_name=person_data.last_name,
            date_of_birth=person_data.date_of_birth,
            email=person_data.email,
            phone=person_data.phone,
            nationality=person_data.nationality,
            passport_number=person_data.passport_number,
            passport_expiry=person_data.passport_expiry,
            address=person_data.address or {},
            personal_info=person_data.personal_info or {},
            immigration_history=person_data.immigration_history or {},
            education=person_data.education or {},
            work_experience=person_data.work_experience or {},
            language_scores=person_data.language_scores or {},
            family_info=person_data.family_info or {},
        )
        db.add(person)
        db.commit()
        db.refresh(person)
        return person

    @staticmethod
    def get_person_by_id(
        db: Session, person_id: Union[str, uuid.UUID], org_id: Union[str, uuid.UUID]
    ) -> Optional[Person]:
        person_id_str = str(person_id)
        org_id_str = str(org_id)
        return (
            db.query(Person)
            .filter(
                Person.id == person_id_str,
                Person.org_id == org_id_str,
                Person.deleted_at.is_(None),
            )
            .first()
        )

    @staticmethod
    def get_persons_by_org(
        db: Session, org_id: str, skip: int = 0, limit: int = 100
    ) -> list[Person]:
        return (
            db.query(Person)
            .filter(Person.org_id == org_id, Person.deleted_at.is_(None))
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def update_person(
        db: Session, person_id: str, org_id: str, person_data: PersonUpdate
    ) -> Optional[Person]:
        person = PersonService.get_person_by_id(db, person_id, org_id)
        if not person:
            return None

        update_data = person_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(person, field, value)

        person.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(person)
        return person

    @staticmethod
    def delete_person(db: Session, person_id: str, org_id: str) -> bool:
        person = PersonService.get_person_by_id(db, person_id, org_id)
        if not person:
            return False

        person.deleted_at = datetime.utcnow()
        db.commit()
        return True

    @staticmethod
    def search_persons(
        db: Session, org_id: str, query: str, skip: int = 0, limit: int = 100
    ) -> list[Person]:
        return (
            db.query(Person)
            .filter(
                Person.org_id == org_id,
                Person.deleted_at.is_(None),
                (
                    Person.first_name.ilike(f"%{query}%")
                    | Person.last_name.ilike(f"%{query}%")
                    | Person.email.ilike(f"%{query}%")
                ),
            )
            .offset(skip)
            .limit(limit)
            .all()
        )
