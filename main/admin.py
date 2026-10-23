import csv

from django.contrib import admin
from django.http import HttpResponse
from django.urls import reverse
from django.utils import timezone

from .models import EmailInstitucional


@admin.register(EmailInstitucional)
class EmailInstitucionalAdmin(admin.ModelAdmin):
    list_display = (
        "email",
        "responsavel",
        "setor",
        "criado_em",
        "expira_em",
        "respondido_em",
        "revogado",
    )

    search_fields = ("email", "responsavel", "setor")

    list_filter = (
        "revogado",
        "criado_em",
        "expira_em",
        "respondido_em",
    )

    readonly_fields = (
        "token",
        "criado_em",
        "respondido_em",
    )

    ordering = ("email",)

    actions = ["exportar_todos_emails"]

    @admin.action(
        description="Exportar TODOS os e-mails cadastrados para CSV"
    )
    def exportar_todos_emails(self, request, queryset):
        resposta = HttpResponse(
            content_type="text/csv; charset=utf-8"
        )

        resposta["Content-Disposition"] = (
            'attachment; filename="emails_institucionais.csv"'
        )

        # BOM para facilitar a abertura no Excel.
        resposta.write("\ufeff")

        escritor = csv.writer(resposta, delimiter=";")

        escritor.writerow([
            "E-mail",
            "Token",
            "Link de confirmação",
            "Criado em",
            "Expira em",
            "Responsável",
            "Setor",
            "Respondido em",
            "Revogado",
        ])

        # Busca TODOS os registros, independentemente
        # da seleção feita na tela ou da paginação.
        registros = EmailInstitucional.objects.all().order_by("email")

        for registro in registros:
            caminho = reverse(
                "main:confirmar_email",
                args=[registro.token],
            )

            link = request.build_absolute_uri(caminho)

            criado_em = (
                timezone.localtime(registro.criado_em).strftime(
                    "%d/%m/%Y %H:%M"
                )
                if registro.criado_em
                else ""
            )

            expira_em = (
                timezone.localtime(registro.expira_em).strftime(
                    "%d/%m/%Y %H:%M"
                )
                if registro.expira_em
                else ""
            )

            respondido_em = (
                timezone.localtime(registro.respondido_em).strftime(
                    "%d/%m/%Y %H:%M"
                )
                if registro.respondido_em
                else ""
            )

            escritor.writerow([
                registro.email,
                registro.token,
                link,
                criado_em,
                expira_em,
                registro.responsavel,
                registro.setor,
                respondido_em,
                "Sim" if registro.revogado else "Não",
            ])

        return resposta