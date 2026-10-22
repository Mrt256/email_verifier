from django.db import transaction
from django.http import Http404
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from .models import EmailInstitucional


TEMPLATE_CONFIRM = "main/pages/confirm.html"


@require_http_methods(["GET", "POST"])
def confirmar_email(request, token):
    registro = get_object_or_404(EmailInstitucional, token=token)

    if request.method == "GET":
        return render(
            request,
            TEMPLATE_CONFIRM,
            {
                "registro": registro,
                "ja_respondido": registro.respondido_em is not None,
            },
        )

    responsavel = request.POST.get("responsavel", "").strip()
    setor = request.POST.get("setor", "").strip()

    if (
        not responsavel
        or not setor
        or len(responsavel) > 150
        or len(setor) > 150
    ):
        return render(
            request,
            TEMPLATE_CONFIRM,
            {
                "registro": registro,
                "erro": "Informe um nome e um setor válidos (até 150 caracteres cada).",
            },
            status=400,
        )

    with transaction.atomic():
        atualizados = EmailInstitucional.objects.filter(
            pk=registro.pk,
            respondido_em__isnull=True,
        ).update(
            responsavel=responsavel,
            setor=setor,
            respondido_em=timezone.now(),
        )

    registro.refresh_from_db()

    if atualizados == 0:
        return render(
            request,
            TEMPLATE_CONFIRM,
            {
                "registro": registro,
                "ja_respondido": True,
            },
        )

    return render(
        request,
        TEMPLATE_CONFIRM,
        {
            "registro": registro,
            "sucesso": True,
        },
    )
