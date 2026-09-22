"""Service for booking, updating and cancelling appointments."""
from sqlalchemy.orm import Session

from app.models.cita import Cita, EstadoCita
from app.models.historial_cita import HistorialCita
from app.models.paciente import Paciente
from app.models.slot_disponibilidad import SlotDisponibilidad, SlotEstado
from app.schemas.cita import CitaCreateRequest, CitaUpdateRequest, CitaResponse


class CitaService:
    """Business rules for citas."""

    @staticmethod
    def _build_response(cita: Cita, slot: SlotDisponibilidad, paciente: Paciente) -> CitaResponse:
        return CitaResponse(
            id_cita=cita.id_cita,
            estado_actual=cita.estado_actual.value if hasattr(cita.estado_actual, "value") else str(cita.estado_actual),
            notas_paciente=cita.notas_paciente,
            creado_en=cita.creado_en,
            paciente={
                "id_paciente": paciente.id_paciente,
                "nombre": paciente.nombre,
                "apellido": paciente.apellido,
                "telefono_whatsapp": paciente.telefono_whatsapp,
                "email": paciente.email,
            },
            slot={
                "id_slot": slot.id_slot,
                "id_doctor": slot.id_doctor,
                "id_clinica": slot.id_clinica,
                "fecha_hora_inicio": slot.fecha_hora_inicio,
                "fecha_hora_fin": slot.fecha_hora_fin,
            },
        )

    @staticmethod
    def create_cita(db: Session, request: CitaCreateRequest) -> CitaResponse:
        slot = (
            db.query(SlotDisponibilidad)
            .filter(SlotDisponibilidad.id_slot == request.id_slot)
            .with_for_update()
            .first()
        )
        if not slot:
            raise LookupError(f"Slot con ID {request.id_slot} no encontrado")
        if slot.estado != SlotEstado.DISPONIBLE:
            raise ValueError("El slot seleccionado no está disponible")

        paciente = (
            db.query(Paciente)
            .filter(Paciente.telefono_whatsapp == request.paciente.telefono_whatsapp)
            .first()
        )
        if not paciente:
            paciente = Paciente(
                nombre=request.paciente.nombre,
                apellido=request.paciente.apellido,
                telefono_whatsapp=request.paciente.telefono_whatsapp,
                email=request.paciente.email,
            )
            db.add(paciente)
            db.flush()
        else:
            paciente.nombre = request.paciente.nombre
            paciente.apellido = request.paciente.apellido
            paciente.email = request.paciente.email

        cita = Cita(
            id_slot=slot.id_slot,
            id_paciente=paciente.id_paciente,
            estado_actual=EstadoCita.PROGRAMADA,
            notas_paciente=request.notas_paciente,
        )
        db.add(cita)
        slot.estado = SlotEstado.RESERVADO
        db.flush()

        historial = HistorialCita(
            id_cita=cita.id_cita,
            estado_anterior=None,
            estado_nuevo="PROGRAMADA",
            cambiado_por="PACIENTE_BOT",
            comentario="Cita agendada desde API",
        )
        db.add(historial)

        try:
            db.commit()
        except Exception as exc:
            db.rollback()
            raise RuntimeError(f"No se pudo agendar la cita: {exc}") from exc

        db.refresh(cita)
        db.refresh(slot)
        db.refresh(paciente)
        return CitaService._build_response(cita, slot, paciente)

    @staticmethod
    def update_cita(db: Session, id_cita: int, request: CitaUpdateRequest) -> CitaResponse:
        cita = db.query(Cita).filter(Cita.id_cita == id_cita).with_for_update().first()
        if not cita:
            raise LookupError(f"Cita con ID {id_cita} no encontrada")
        if cita.estado_actual == EstadoCita.CANCELADA:
            raise ValueError("No se puede modificar una cita cancelada")

        slot_actual = db.query(SlotDisponibilidad).filter(SlotDisponibilidad.id_slot == cita.id_slot).first()
        if not slot_actual:
            raise LookupError("No se encontró el slot actual de la cita")

        if request.id_slot and request.id_slot != cita.id_slot:
            nuevo_slot = (
                db.query(SlotDisponibilidad)
                .filter(SlotDisponibilidad.id_slot == request.id_slot)
                .with_for_update()
                .first()
            )
            if not nuevo_slot:
                raise LookupError(f"Slot con ID {request.id_slot} no encontrado")
            if nuevo_slot.estado != SlotEstado.DISPONIBLE:
                raise ValueError("El nuevo slot no está disponible")

            slot_actual.estado = SlotEstado.DISPONIBLE
            nuevo_slot.estado = SlotEstado.RESERVADO
            cita.id_slot = nuevo_slot.id_slot
            slot_actual = nuevo_slot

        if request.notas_paciente is not None:
            cita.notas_paciente = request.notas_paciente

        estado_anterior = cita.estado_actual.value
        estado_nuevo = estado_anterior

        if request.estado_actual is not None:
            estados_validos = {estado.value for estado in EstadoCita}
            if request.estado_actual not in estados_validos:
                raise ValueError(
                    f"estado_actual inválido: '{request.estado_actual}'. "
                    f"Valores permitidos: {sorted(estados_validos)}"
                )

            nuevo_estado_enum = EstadoCita(request.estado_actual)
            cita.estado_actual = nuevo_estado_enum
            estado_nuevo = nuevo_estado_enum.value

            # Si la cita se cancela o marca como no asistida, liberar el slot
            if nuevo_estado_enum in (EstadoCita.CANCELADA, EstadoCita.NO_ASISTIO):
                slot_actual.estado = SlotEstado.DISPONIBLE

        db.add(
            HistorialCita(
                id_cita=cita.id_cita,
                estado_anterior=estado_anterior,
                estado_nuevo=estado_nuevo,
                cambiado_por="PACIENTE_BOT",
                comentario="Cita actualizada desde API",
            )
        )

        try:
            db.commit()
        except Exception as exc:
            db.rollback()
            raise RuntimeError(f"No se pudo actualizar la cita: {exc}") from exc

        paciente = db.query(Paciente).filter(Paciente.id_paciente == cita.id_paciente).first()
        db.refresh(cita)
        db.refresh(slot_actual)
        return CitaService._build_response(cita, slot_actual, paciente)

    @staticmethod
    def delete_cita(db: Session, id_cita: int) -> bool:
        cita = db.query(Cita).filter(Cita.id_cita == id_cita).with_for_update().first()
        if not cita:
            raise LookupError(f"Cita con ID {id_cita} no encontrada")

        slot = db.query(SlotDisponibilidad).filter(SlotDisponibilidad.id_slot == cita.id_slot).first()
        if slot:
            slot.estado = SlotEstado.DISPONIBLE

        db.add(
            HistorialCita(
                id_cita=cita.id_cita,
                estado_anterior=cita.estado_actual.value,
                estado_nuevo="CANCELADA",
                cambiado_por="PACIENTE_BOT",
                comentario="Cita eliminada desde API",
            )
        )
        cita.estado_actual = EstadoCita.CANCELADA

        try:
            db.commit()
        except Exception as exc:
            db.rollback()
            raise RuntimeError(f"No se pudo eliminar la cita: {exc}") from exc

        return True
