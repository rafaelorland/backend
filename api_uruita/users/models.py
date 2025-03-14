
import random
import string
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.core.validators import  RegexValidator

from users.services import validate_cpf


class CustomUser(AbstractUser): 
    """
    Modelo para customização de usuário no django
    """

    email = models.EmailField(unique=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    cpf = models.CharField(
        max_length=14, 
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^\d{3}\.\d{3}\.\d{3}-\d{2}$',
                message="O CPF deve estar no formato XXX.XXX.XXX-XX" 
            ),
            validate_cpf 
        ]
    ) 
    phone_numbe = models.CharField(max_length=15, blank=True, null=True)
    is_verified_email = models.BooleanField(default=False) 
    verification_code = models.CharField(max_length=4, blank=True, null=True)

    groups = models.ManyToManyField(Group, related_name="customuser_groups", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="customuser_permissions", blank=True)

    USERNAME_FIELD = 'cpf' 
    REQUIRED_FIELDS = ['username','email']

    def generate_verification_code(self):
        """
        Gera um código de verificação aleatório
        """

        self.verification_code = ''.join(random.choices(string.digits, k=4))
        self.save()

    def __str__(self):
        return self.cpf 
