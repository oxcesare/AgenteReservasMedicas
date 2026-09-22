"""Doctor availability endpoints."""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import (
    DoctorAvailabilityResponse,
    CreateAvailabilityRequest,
    SlotCreatedResponse,
    SlotUpdateRequest,
    SlotDetailResponse,
)
from app.services import AvailabilityService, SlotCreationService

router = APIRouter(prefix="/api/doctors", tags=["availability"])


@router.get("/{id_doctor}/availability", response_model=DoctorAvailabilityResponse)
def get_doctor_availability(
    id_doctor: int,
    desde: datetime | None = Query(default=None),
    hasta: datetime | None = Query(default=None),
    pagina: int = Query(default=1, ge=1),
    tamano_pagina: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """Return all slots for a doctor in the date range, including their state.

    Slots RESERVADOS incluyen el detalle de la cita y el paciente asociado.
    """
    try:
        return AvailabilityService.get_doctor_availability(
            db,
            id_doctor,
            desde,
            hasta,
            pagina,
            tamano_pagina,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/{id_doctor}/availability", response_model=SlotCreatedResponse, status_code=201)
def create_doctor_availability(
    id_doctor: int,
    request: CreateAvailabilityRequest,
    db: Session = Depends(get_db),
):
    """Create availability slots for a doctor.
    
    Doctor can create multiple slots in one request for one or more days.
    """
    # Validate id_doctor matches
    if id_doctor != request.id_doctor:
        raise HTTPException(
            status_code=400,
            detail="El id_doctor en la URL debe coincidir con el del cuerpo de la solicitud"
        )
    
    try:
        result = SlotCreationService.create_slots(db, request)
        return SlotCreatedResponse(**result)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.put("/{id_doctor}/availability/{id_slot}", response_model=SlotDetailResponse)
def update_doctor_slot(
    id_doctor: int,
    id_slot: int,
    request: SlotUpdateRequest,
    db: Session = Depends(get_db),
):
    """Update a doctor's available slot."""
    try:
        slot = SlotCreationService.update_slot(db, id_doctor, id_slot, request)
        return SlotDetailResponse(
            id_slot=slot.id_slot,
            id_doctor=slot.id_doctor,
            id_clinica=slot.id_clinica,
            fecha_hora_inicio=slot.fecha_hora_inicio,
            fecha_hora_fin=slot.fecha_hora_fin,
            estado=slot.estado.value if hasattr(slot.estado, "value") else str(slot.estado),
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.delete("/{id_doctor}/availability/{id_slot}", status_code=204)
def delete_doctor_slot(
    id_doctor: int,
    id_slot: int,
    db: Session = Depends(get_db),
):
    """Delete a doctor's available slot."""
    try:
        SlotCreationService.delete_slot(db, id_doctor, id_slot)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
