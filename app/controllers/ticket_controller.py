
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.dependencies import get_db, get_current_user, require_staff
from app.models.user import User
from app.models.category import Category
from app.models.location import Location
from app.models.ticket import Ticket
from app.models.ticket_history import TicketHistory
from app.schemas.ticket import TicketCreate, TicketRead, TicketStatusUpdate, TicketStatus


router = APIRouter(prefix="/tickets", tags=["Заявки"])



@router.post("/", response_model=TicketRead, status_code=201)
def create_ticket(
    payload: TicketCreate,
    db: Session = Depends(get_db)
):
    if payload.category_id is not None:
        category = db.get(Category, payload.category_id)

        if category is None:
            raise HTTPException(
                status_code=404,
                detail="Категория не найдена"
            )

    if payload.location_id is not None:
        location = db.get(Location, payload.location_id)

        if location is None:
            raise HTTPException(
                status_code=404,
                detail="Помещение не найдено"
            )

    ticket = Ticket(
        title=payload.title,
        description=payload.description,
        category_id=payload.category_id,
        location_id=payload.location_id,
        user_id=None,
        status="Новая"
    )

    db.add(ticket)
    db.flush()

    history = TicketHistory(
        ticket_id=ticket.id,
        old_status=None,
        new_status="Новая",
        changed_by=None
    )

    db.add(history)
    db.commit()
    db.refresh(ticket)

    return ticket






@router.get("/", response_model=list[TicketRead])
def get_tickets(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    status_filter: TicketStatus | None = Query(default=None, alias="status"),
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0
):
    query = (
        select(
            Ticket,
            Category.name,
            Location.room_number
        )
        .outerjoin(Category, Ticket.category_id == Category.id)
        .outerjoin(Location, Ticket.location_id == Location.id)
    )

    if user.role == "student":
        query = query.where(Ticket.user_id == user.id)

    if status_filter is not None:
        query = query.where(Ticket.status == status_filter)

    query = (
        query
        .order_by(Ticket.created_at.desc())
        .limit(limit)
        .offset(offset)
    )

    results = db.execute(query).all()

    tickets = []

    for ticket, category_name, location_name in results:
        ticket_data = TicketRead.model_validate(ticket).model_dump()

        ticket_data["category_name"] = category_name
        ticket_data["location_name"] = location_name

        tickets.append(ticket_data)

    return tickets

  


@router.get("/{ticket_id}", response_model=TicketRead)
def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    ticket = db.get(Ticket, ticket_id)

    if ticket is None:
        raise HTTPException(status_code=404, detail="Заявка не найдена")

    if user.role == "student" and ticket.user_id != user.id:
        raise HTTPException(status_code=404, detail="Заявка не найдена")

    return ticket


@router.patch("/{ticket_id}/status", response_model=TicketRead)
def update_ticket_status(
    ticket_id: int,
    payload: TicketStatusUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_staff)
):
    ticket = db.get(Ticket, ticket_id)

    if ticket is None:
        raise HTTPException(status_code=404, detail="Заявка не найдена")

    old_status = ticket.status

    if old_status == payload.status:
        return ticket

    ticket.status = payload.status
    ticket.updated_at = datetime.now()

    history = TicketHistory(
        ticket_id=ticket.id,
        old_status=old_status,
        new_status=payload.status,
        changed_by=user.id
    )

    db.add(history)
    db.commit()
    db.refresh(ticket)

    return ticket
