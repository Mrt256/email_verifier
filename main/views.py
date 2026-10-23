from django.db import transaction
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from .models import EmailInstitucional


TEMPLATE_CONFIRM = "main/pages/confirm.html"


@require_http_methods(["GET", "POST"])
def confirmar_email(request, token):
    registro = get_object_or_404(
        EmailInstitucional,
        token=token,
    )

    # Se já foi respondido, não permitir nova resposta.
    if registro.respondido_em is not None:
        return render(
            request,
            TEMPLATE_CONFIRM,
            {
                "registro": registro,
                "ja_respondido": True,
            },
        )

    # Bloquear links revogados ou expirados.
    if registro.revogado or registro.expira_em <= timezone.now():
        return render(
            request,
            TEMPLATE_CONFIRM,
            {
                "registro": registro,
                "link_invalido": True,
            },
            status=410,
        )

    if request.method == "GET":
        return render(
            request,
            TEMPLATE_CONFIRM,
            {
                "registro": registro,
                "ja_respondido": False,
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
                "erro": (
                    "Informe um nome e um setor válidos "
                    "(até 150 caracteres cada)."
                ),
            },
            status=400,
        )

    agora = timezone.now()

    # Atualizar somente se o link continuar válido
    # e ainda não tiver sido respondido.
    with transaction.atomic():
        atualizados = EmailInstitucional.objects.filter(
            pk=registro.pk,
            respondido_em__isnull=True,
            revogado=False,
            expira_em__gt=agora,
        ).update(
            responsavel=responsavel,
            setor=setor,
            respondido_em=agora,
        )

    registro.refresh_from_db()

    if atualizados == 0:
        # Verificar novamente o estado atual do registro.
        if registro.respondido_em is not None:
            contexto = {
                "registro": registro,
                "ja_respondido": True,
            }
        else:
            contexto = {
                "registro": registro,
                "link_invalido": True,
            }

        return render(
            request,
            TEMPLATE_CONFIRM,
            contexto,
            status=410 if registro.respondido_em is None else 200,
        )

    return render(
        request,
        TEMPLATE_CONFIRM,
        {
            "registro": registro,
            "sucesso": True,
        },
    )