"""Appointment booking endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.cita import CitaCreateRequest, CitaResponse, CitaUpdateRequest
from app.services.cita_service import CitaService

router = APIRouter(prefix="/api/citas", tags=["citas"])


@router.post("", response_model=CitaResponse, status_code=201)
def create_cita(request: CitaCreateRequest, db: Session = Depends(get_db)):
    """Book an appointment for a patient."""
    try:
        return CitaService.create_cita(db, request)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.put("/{id_cita}", response_model=CitaResponse)
def update_cita(id_cita: int, request: CitaUpdateRequest, db: Session = Depends(get_db)):
    """Change the selected slot or notes of an existing appointment."""
    try:
        return CitaService.update_cita(db, id_cita, request)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.delete("/{id_cita}", status_code=204)
def delete_cita(id_cita: int, db: Session = Depends(get_db)):
    """Cancel a booked appointment and release its slot."""
    try:
        CitaService.delete_cita(db, id_cita)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
