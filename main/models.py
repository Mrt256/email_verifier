import secrets
from datetime import timedelta

from django.db import models
from django.utils import timezone


def gerar_token():
    return secrets.token_urlsafe(32)


def calcular_expiracao_token():
    return timezone.now() + timedelta(days=7)


class EmailInstitucional(models.Model):
    email = models.EmailField(unique=True)

    token = models.CharField(
        max_length=64,
        unique=True,
        default=gerar_token,
        editable=False,
    )

    responsavel = models.CharField(
        max_length=150,
        blank=True,
    )

    setor = models.CharField(
        max_length=150,
        blank=True,
    )

    criado_em = models.DateTimeField(auto_now_add=True)

    respondido_em = models.DateTimeField(
        null=True,
        blank=True,
    )

    # O link expira 7 dias após a geração do token.
    expira_em = models.DateTimeField(
        default=calcular_expiracao_token,
    )

    # Permite invalidar o link antes da expiração.
    revogado = models.BooleanField(default=False)

    class Meta:
        ordering = ["email"]
        verbose_name = "E-mail institucional"
        verbose_name_plural = "E-mails institucionais"

    def __str__(self):
        return self.email