from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List
from app.models.auth_user import Role, UserAuth

def create(db: Session, name: str, hashed_password: str, roles: List[Role]):
    try:
        db.add(UserAuth( name = name, hashed_password = hashed_password, roles = roles))
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    

def get_by_name(db: Session, name: str):
    query = select(UserAuth).where(UserAuth.name == name)
    user = db.execute(query).scalar_one_or_none()
    return user

def get_roles(db: Session, name: str):
    query = select(UserAuth.roles).where(UserAuth.name == name)
    user_roles = db.execute(query)
    return user_roles