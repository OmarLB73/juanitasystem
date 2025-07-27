from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
# from proyect.models import Evento
from proyect.utils import enviar_notificacion_push

class Command(BaseCommand):
    help = 'Envía notificaciones 30 minutos antes de cada evento'

    def handle(self, *args, **kwargs):

        status, respuesta = enviar_notificacion_push(
                titulo="Recordatorio de evento",
                mensaje="Primer mensaje de prueba",
                user_ids= [1]
            )

        if status == 200:
            self.stdout.write(self.style.SUCCESS(f"Notificado: Usuario"))
        else:
            self.stdout.write(self.style.ERROR(f"Error: {respuesta}"))


        # ahora = timezone.now()
        # en_30_min = ahora + timedelta(minutes=30)

        # eventos = Evento.objects.filter(
        #     fecha_hora__range=(ahora, en_30_min),
        #     notificado=False
        # )

        # for evento in eventos:
        #     usuario = evento.usuario
        #     mensaje = f"Tienes un evento: '{evento.titulo}' en 30 minutos."

        #     status, respuesta = enviar_notificacion_push(
        #         titulo="Recordatorio de evento",
        #         mensaje=mensaje,
        #         user_ids=[usuario.id]
        #     )

        #     if status == 200:
        #         evento.notificado = True
        #         evento.save()
        #         self.stdout.write(self.style.SUCCESS(f"Notificado: {usuario.username}"))
        #     else:
        #         self.stdout.write(self.style.ERROR(f"Error: {respuesta}"))
