from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.models.category import Category
from app.schemas.category import CategoryRead


router = APIRouter(
    prefix="/categories",
    tags=["Категории"]
)


@router.get("/", response_model=list[CategoryRead])
def get_categories(db: Session = Depends(get_db)):
    query = select(Category).order_by(Category.id)

    categories = db.scalars(query).all()

    return categories
