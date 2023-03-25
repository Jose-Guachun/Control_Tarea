from django.core.mail import EmailMultiAlternatives
from django.http import HttpResponse
from django.template.loader import get_template
from django.conf import settings
from django.shortcuts import render
from django.template.loader import render_to_string

def send_email(persona, qr_url,data, lector_qr):
    context={'persona': persona, 'qr_url': qr_url,'data':data, 'lector_qr': lector_qr}

    # template=get_template('correo.html')
    # content=template.render(context)
    content = render_to_string('correo.html', context)
    email=EmailMultiAlternatives(
        'School, Codigo QR de tarea',
        'Tarea asignada',
        settings.EMAIL_HOST_USER,
        [persona.correo]
    )
    email.attach_alternative(content, 'text/html')
    email.send()
    return HttpResponse('Correo enviado exitosamente')