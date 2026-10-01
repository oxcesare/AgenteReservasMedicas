"""
Servicio para enviar mensajes salientes por la API de WhatsApp (Cloud API)
Ubicación: app/services/agent/whatsapp_service.py
"""
import requests
from app.config import settings


def enviar_mensaje(to: str, texto: str) -> None:
    """
    Envía un mensaje de texto libre por WhatsApp.
    Solo funciona dentro de la ventana de 24h desde el último mensaje
    del usuario (fuera de esa ventana se necesitaría un template aprobado).

    to: número del destinatario, formato E.164 sin '+' (ej. '5212281044727')
    texto: contenido del mensaje
    """
    url = f"https://graph.facebook.com/v21.0/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"

    headers = {
        "Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": texto},
    }

    resp = requests.post(url, headers=headers, json=payload, timeout=10)

    if resp.status_code != 200:
        # No lanzamos excepción para no tumbar el webhook completo por un
        # fallo al mandar la respuesta; solo lo dejamos loggeado.
        print(f"[whatsapp_service] Error al enviar mensaje a {to}: "
              f"{resp.status_code} - {resp.text}")