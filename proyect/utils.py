import requests
from django.conf import settings

def enviar_notificacion_push(titulo, mensaje, user_ids):
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Authorization": f"Basic {settings.ONESIGNAL_API_KEY}"
    }

    payload = {
        "app_id": settings.ONESIGNAL_APP_ID,
        "headings": {"en": titulo},
        "contents": {"en": mensaje},
        "include_external_user_ids": [str(uid) for uid in user_ids],
        "channel_for_external_user_ids": "push"
    }

    r = requests.post("https://onesignal.com/api/v1/notifications", json=payload, headers=headers)
    return r.status_code, r.json()
