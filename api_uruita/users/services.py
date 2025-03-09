from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

def validate_cpf(value):
    """
    Valida um CPF com base no formato e nos dígitos verificadores.
    """
    import re
    cpf = re.sub(r'[^0-9]', '', value)

    if len(cpf) != 11 or cpf == cpf[0] * 11:
        raise ValidationError("CPF inválido")

    def calcular_dv(digitos):
        """
        "https://www.campuscode.com.br/conteudos/o-calculo-do-digito-verificador-do-cpf-e-do-cnpj"
        """
        
        soma = sum(int(digitos[i]) * (10 - i) for i in range(9))
        dv1 = (soma * 10) % 11
        dv1 = dv1 if dv1 < 10 else 0

        soma = sum(int(digitos[i]) * (11 - i) for i in range(10))
        dv2 = (soma * 10) % 11
        dv2 = dv2 if dv2 < 10 else 0

        return dv1, dv2

    dv1, dv2 = calcular_dv(cpf)
    if int(cpf[9]) != dv1 or int(cpf[10]) != dv2:
        raise ValidationError("CPF inválido")



def send_verification_email(user):
    """
    Envia um e-mail de verificação com um código de ativação para o usuário.
    """
    
    subject = "Confirmação de Cadastro"
    context = {"username": user.username, "verification_code": user.verification_code}
    
    html_message = render_to_string("emails/verificar_email.html", context)
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=html_message,
        fail_silently=False,
    )