"""Availability service."""
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models.doctor import Doctor
from app.models.cita import Cita
from app.models.paciente import Paciente
from app.models.slot_disponibilidad import SlotDisponibilidad, SlotEstado
from app.schemas.availability import (
    AvailabilitySlot,
    AvailabilityCita,
    AvailabilityCitaPaciente,
    DoctorAvailabilityResponse,
)


class AvailabilityService:
    """Business logic for doctor availability."""

    @staticmethod
    def get_doctor_availability(
        db: Session,
        id_doctor: int,
        desde: datetime | None = None,
        hasta: datetime | None = None,
        pagina: int = 1,
        tamano_pagina: int = 50,
    ) -> DoctorAvailabilityResponse:
        start = desde or datetime.utcnow()
        end = hasta or (start + timedelta(days=7))

        if end <= start:
            raise ValueError("'hasta' debe ser mayor que 'desde'")
        if pagina < 1:
            raise ValueError("'pagina' debe ser mayor o igual a 1")
        if tamano_pagina < 1:
            raise ValueError("'tamano_pagina' debe ser mayor o igual a 1")

        doctor = db.query(Doctor).filter(Doctor.id_doctor == id_doctor).first()
        if not doctor:
            raise LookupError("Doctor no encontrado")

        base_query = (
            db.query(SlotDisponibilidad)
            .filter(SlotDisponibilidad.id_doctor == id_doctor)
            .filter(SlotDisponibilidad.fecha_hora_inicio < end)
            .filter(SlotDisponibilidad.fecha_hora_fin > start)
            .order_by(SlotDisponibilidad.fecha_hora_inicio.asc())
        )

        total_slots = base_query.count()
        offset = (pagina - 1) * tamano_pagina
        slots = base_query.offset(offset).limit(tamano_pagina).all()

        # Cargar en un solo query las citas (con paciente) asociadas a los slots reservados
        slot_ids_reservados = [
            slot.id_slot for slot in slots if slot.estado == SlotEstado.RESERVADO
        ]
        citas_por_slot: dict[int, tuple[Cita, Paciente]] = {}
        if slot_ids_reservados:
            filas = (
                db.query(Cita, Paciente)
                .join(Paciente, Paciente.id_paciente == Cita.id_paciente)
                .filter(Cita.id_slot.in_(slot_ids_reservados))
                .all()
            )
            citas_por_slot = {cita.id_slot: (cita, paciente) for cita, paciente in filas}

        slot_items = []
        for slot in slots:
            estado_str = slot.estado.value if hasattr(slot.estado, "value") else str(slot.estado)

            cita_data = None
            if slot.estado == SlotEstado.RESERVADO:
                par = citas_por_slot.get(slot.id_slot)
                if par:
                    cita, paciente = par
                    cita_data = AvailabilityCita(
                        id_cita=cita.id_cita,
                        estado_actual=(
                            cita.estado_actual.value
                            if hasattr(cita.estado_actual, "value")
                            else str(cita.estado_actual)
                        ),
                        notas_paciente=cita.notas_paciente,
                        paciente=AvailabilityCitaPaciente(
                            id_paciente=paciente.id_paciente,
                            nombre=paciente.nombre,
                            apellido=paciente.apellido,
                            telefono_whatsapp=paciente.telefono_whatsapp,
                            email=paciente.email,
                        ),
                    )

            slot_items.append(
                AvailabilitySlot(
                    id_slot=slot.id_slot,
                    id_clinica=slot.id_clinica,
                    fecha_hora_inicio=slot.fecha_hora_inicio,
                    fecha_hora_fin=slot.fecha_hora_fin,
                    estado=estado_str,
                    cita=cita_data,
                )
            )

        return DoctorAvailabilityResponse(
            id_doctor=id_doctor,
            desde=start,
            hasta=end,
            pagina=pagina,
            tamano_pagina=tamano_pagina,
            total_slots=total_slots,
            slots=slot_items,
        )
