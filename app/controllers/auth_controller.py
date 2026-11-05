
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from typing import Annotated
from app.db.dependencies import get_db, get_current_user, require_admin

from app.models.user import User
from app.schemas.user import UserRegister, UserLogin, UserRead, TokenRead
from app.services.auth_service import (
    hash_password,
    verify_password,
    create_access_token
)


router = APIRouter(
    prefix="/auth",
    tags=["Авторизация"]
)


@router.post("/register", response_model=UserRead, status_code=201)
def register_user(
    payload: UserRegister,
    admin: Annotated[User, Depends(require_admin)],
    db: Session = Depends(get_db)
):
    email = payload.email.strip().lower()

    if "@" not in email:
        raise HTTPException(
            status_code=422,
            detail="Укажите корректный email"
        )

    existing_user = db.scalar(
        select(User).where(User.email == email)
    )

    if existing_user is not None:
        raise HTTPException(
            status_code=409,
            detail="Пользователь с таким email уже существует"
        )

    user = User(
        full_name=payload.full_name.strip(),
        email=email,
        password=hash_password(payload.password),
        role="employee"
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@router.post("/login", response_model=TokenRead)
def login_user(
    payload: UserLogin,
    db: Session = Depends(get_db)
):
    email = payload.email.strip().lower()

    user = db.scalar(
        select(User).where(User.email == email)
    )

    if (
        user is None
        or not verify_password(payload.password, user.password)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль"
        )

    token = create_access_token(user.id)

    return TokenRead(access_token=token)


@router.get("/me", response_model=UserRead)
def read_current_user(
    user: Annotated[User, Depends(get_current_user)]
):
    return user
