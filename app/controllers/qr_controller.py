
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.templating import Jinja2Templates
from fastapi import Request
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.models.location import Location
from app.models.category import Category


router = APIRouter(tags=["QR-коды"])

BASE_DIR = Path(__file__).resolve().parent.parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@router.get("/tickets/create")
def create_ticket_page(
    request: Request,
    location_id: int | None = Query(default=None, gt=0),
    db: Session = Depends(get_db)
):
    room_number = None

    if location_id is not None:
        location = db.get(Location, location_id)

        if location is None:
            raise HTTPException(
                status_code=404,
                detail="Помещение не найдено"
            )

        room_number = location.room_number

    categories = db.query(Category).order_by(Category.name).all()

    assistant_url = (
        f"/assistant/?location_id={location_id}"
        if location_id is not None
        else "/assistant/"
    )

    return templates.TemplateResponse(
        "ticket-form.html",
        {
            "request": request,
            "room_number": room_number,
            "location_id": location_id,
            "categories": categories,
            "assistant_url": assistant_url
        }
    )
