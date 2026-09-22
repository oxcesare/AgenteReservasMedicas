"""Service to create, update and delete doctor availability slots."""
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.slot_disponibilidad import SlotDisponibilidad, SlotEstado
from app.models.doctor import Doctor
from app.schemas.slot_create import CreateAvailabilityRequest, SlotUpdateRequest


class SlotCreationService:
    """Service for creating doctor availability slots."""

    @staticmethod
    def create_slots(
        db: Session,
        request: CreateAvailabilityRequest
    ) -> dict:
        """
        Create multiple availability slots for a doctor.
        
        Args:
            db: Database session
            request: Request with doctor ID, clinic ID, and list of days with time slots
            
        Returns:
            Dictionary with count and details of created slots
        """
        id_doctor = request.id_doctor
        id_clinica = request.id_clinica
        
        # Validate doctor exists
        doctor = db.query(Doctor).filter(Doctor.id_doctor == id_doctor).first()
        if not doctor:
            raise LookupError(f"Doctor con ID {id_doctor} no encontrado")
        
        # Validate doctor is active
        if not doctor.activo:
            raise ValueError(f"El doctor {doctor.nombre} {doctor.apellido} no está activo")
        
        slots_creados = []
        slots_count = 0
        
        # Process each day
        for day_availability in request.slots:
            fecha = day_availability.fecha
            
            # Process each time slot for this day
            for franja in day_availability.franjas:
                # Combine date with time to create datetime
                fecha_hora_inicio = datetime.combine(fecha, franja.hora_inicio)
                fecha_hora_fin = datetime.combine(fecha, franja.hora_fin)
                
                # Validate time range
                if fecha_hora_fin <= fecha_hora_inicio:
                    raise ValueError(
                        f"Hora fin debe ser mayor que hora inicio en {fecha}: "
                        f"{franja.hora_inicio} - {franja.hora_fin}"
                    )
                
                # Create slot
                slot = SlotDisponibilidad(
                    id_doctor=id_doctor,
                    id_clinica=id_clinica,
                    fecha_hora_inicio=fecha_hora_inicio,
                    fecha_hora_fin=fecha_hora_fin,
                    estado=SlotEstado.DISPONIBLE
                )
                
                db.add(slot)
                slots_count += 1
                
                slots_creados.append({
                    "fecha": str(fecha),
                    "hora_inicio": str(franja.hora_inicio),
                    "hora_fin": str(franja.hora_fin),
                    "clinica_id": id_clinica
                })
        
        try:
            db.commit()
        except Exception as exc:
            db.rollback()
            raise RuntimeError(f"Error al guardar slots en base de datos: {str(exc)}") from exc
        
        return {
            "id_doctor": id_doctor,
            "id_clinica": id_clinica,
            "total_slots_creados": slots_count,
            "detalles": slots_creados
        }
    
    @staticmethod
    def update_slot(
        db: Session,
        id_doctor: int,
        id_slot: int,
        request: SlotUpdateRequest,
    ) -> SlotDisponibilidad:
        """Update a single slot if it is still available and does not overlap."""
        slot = (
            db.query(SlotDisponibilidad)
            .filter(SlotDisponibilidad.id_slot == id_slot)
            .filter(SlotDisponibilidad.id_doctor == id_doctor)
            .with_for_update()
            .first()
        )

        if not slot:
            raise LookupError(f"Slot con ID {id_slot} no encontrado para el doctor {id_doctor}")

        if slot.estado != SlotEstado.DISPONIBLE:
            raise ValueError(
                f"No se puede modificar un slot en estado {slot.estado}. "
                "Solo se pueden modificar slots DISPONIBLES"
            )

        fecha_hora_inicio = datetime.combine(request.fecha, request.hora_inicio)
        fecha_hora_fin = datetime.combine(request.fecha, request.hora_fin)
        if fecha_hora_fin <= fecha_hora_inicio:
            raise ValueError("La hora_fin debe ser mayor que la hora_inicio")

        clinica_id_objetivo = request.id_clinica if request.id_clinica is not None else slot.id_clinica

        overlapping_slot = (
            db.query(SlotDisponibilidad)
            .filter(SlotDisponibilidad.id_doctor == id_doctor)
            .filter(SlotDisponibilidad.id_slot != id_slot)
            .filter(SlotDisponibilidad.fecha_hora_inicio < fecha_hora_fin)
            .filter(SlotDisponibilidad.fecha_hora_fin > fecha_hora_inicio)
            .first()
        )
        if overlapping_slot:
            raise ValueError(
                "Ya existe otro slot del doctor que se cruza con el horario solicitado"
            )

        slot.id_clinica = clinica_id_objetivo
        slot.fecha_hora_inicio = fecha_hora_inicio
        slot.fecha_hora_fin = fecha_hora_fin

        try:
            db.commit()
        except Exception as exc:
            db.rollback()
            raise RuntimeError(f"Error al actualizar slot en base de datos: {str(exc)}") from exc

        db.refresh(slot)
        return slot

    @staticmethod
    def delete_slot(db: Session, id_doctor: int, id_slot: int) -> bool:
        """Delete a single slot if it's still available."""
        slot = db.query(SlotDisponibilidad).filter(
            SlotDisponibilidad.id_slot == id_slot
        ).filter(
            SlotDisponibilidad.id_doctor == id_doctor
        ).first()
        
        if not slot:
            raise LookupError(f"Slot con ID {id_slot} no encontrado para el doctor {id_doctor}")
        
        if slot.estado != SlotEstado.DISPONIBLE:
            raise ValueError(
                f"No se puede eliminar un slot en estado {slot.estado}. "
                "Solo se pueden eliminar slots DISPONIBLES"
            )
        
        db.delete(slot)
        try:
            db.commit()
        except Exception as exc:
            db.rollback()
            raise RuntimeError(f"Error al eliminar slot en base de datos: {str(exc)}") from exc
        return True
