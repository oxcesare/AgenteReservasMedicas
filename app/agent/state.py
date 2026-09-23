from typing import TypedDict, Optional

class CitaState(TypedDict):
    intencion_confirmada: Optional[bool]
    fecha_solicitada: Optional[str]
    horarios_disponibles: Optional[list[str]]
    horario_elegido: Optional[str]