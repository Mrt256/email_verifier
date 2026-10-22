from django.db import models

import secrets

from django.db import models


def gerar_token():
    return secrets.token_urlsafe(32)


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

    class Meta:
        ordering = ["email"]
        verbose_name = "E-mail institucional"
        verbose_name_plural = "E-mails institucionais"

    def __str__(self):
        return self.email

