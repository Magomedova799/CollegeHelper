
import jwt

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from typing import Annotated

from app.db.database import SessionLocal
from app.models.user import User
from app.services.auth_service import JWT_SECRET_KEY, JWT_ALGORITHM


bearer_scheme = HTTPBearer(auto_error=False)


def get_db():
    with SessionLocal() as db:
        yield db


def get_current_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(bearer_scheme)
    ],
    db: Session = Depends(get_db)
) -> User:

    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Войдите в систему",
        headers={"WWW-Authenticate": "Bearer"}
    )

    if credentials is None:
        raise unauthorized

    try:
        payload = jwt.decode(
            credentials.credentials,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM]
        )

        user_id = int(payload["sub"])

    except (jwt.InvalidTokenError, KeyError, TypeError, ValueError):
        raise unauthorized from None

    user = db.get(User, user_id)

    if user is None:
        raise unauthorized

    return user


def require_staff(
    user: Annotated[User, Depends(get_current_user)]
) -> User:

    if user.role not in {"employee", "admin"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав"
        )

    return user
def require_admin(
    user: Annotated[User, Depends(get_current_user)]
) -> User:

    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешён только администратору"
        )

    return user
