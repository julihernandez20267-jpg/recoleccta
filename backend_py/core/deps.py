from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from typing import Annotated

from database import SessionLocal
from core.config import settings
import models
import schemas

security = HTTPBearer()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

SessionDep = Annotated[Session, Depends(get_db)]
TokenDep = Annotated[HTTPAuthorizationCredentials, Depends(security)]

def get_current_user(db: SessionDep, token: TokenDep) -> models.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token.credentials, settings.JWT_SECRET, algorithms=[settings.ALGORITHM])
        uid_str: str = payload.get("sub")
        if uid_str is None:
            raise credentials_exception
        uid = int(uid_str)
    except JWTError:
        raise credentials_exception
    except ValueError:
        raise credentials_exception

    user = db.query(models.User).filter(models.User.id == uid).first()
    if user is None:
        raise credentials_exception
    return user

def require_role(allowed_roles: list[str]):
    def role_checker(current_user: models.User = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acceso denegado. No tienes permisos suficientes."
            )
        return current_user
    return role_checker

def get_admin_user(current_user: models.User = Depends(require_role(["admin"]))):
    return current_user
