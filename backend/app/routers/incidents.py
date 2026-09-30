import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import get_current_user
from app.models import Incident, User
from app.schemas import IncidentCreate, IncidentOut

router = APIRouter(prefix="/api/incidents", tags=["incidents"])


@router.post("", response_model=IncidentOut, status_code=status.HTTP_201_CREATED)
def create_incident(
    payload: IncidentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Incident:
    incident = Incident(
        user_id=current_user.id,
        title=payload.title,
        description=payload.description,
    )
    db.add(incident)
    db.commit()
    db.refresh(incident)
    return incident


@router.get("", response_model=list[IncidentOut])
def list_incidents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Incident]:
    return db.query(Incident).filter(Incident.user_id == current_user.id).order_by(Incident.created_at.desc()).all()


@router.get("/{incident_id}", response_model=IncidentOut)
def get_incident(
    incident_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Incident:
    incident = db.get(Incident, incident_id)
    # Ownership check: a 404 here (not 403) avoids confirming to an attacker
    # that another user's incident ID exists at all.
    if incident is None or incident.user_id != current_user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Incident not found")
    return incident
