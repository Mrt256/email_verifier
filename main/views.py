from django.shortcuts import render
from django.shortcuts import render, get_object_or_404
from django.utils import timezone

from .models import EmailInstitucional


def confirmar_email(request, token):
    registro = get_object_or_404(
        EmailInstitucional,
        token=token,
    )

    if request.method == "POST":
        # Evita sobrescrever uma confirmação já registrada.
        if registro.respondido_em is not None:
            return render(
                request,
                "main/pages/confirm.html",
                {
                    "registro": registro,
                    "ja_respondido": True,
                },
            )

        responsavel = request.POST.get(
            "responsavel", ""
        ).strip()

        setor = request.POST.get(
            "setor", ""
        ).strip()

        if (
            not responsavel
            or len(responsavel) > 150
            or not setor
            or len(setor) > 150
        ):
            return render(
                request,
                "main/pages/confirm.html",
                {
                    "registro": registro,
                    "erro": "Preencha corretamente os campos solicitados.",
                },
                status=400,
            )

        registro.responsavel = responsavel
        registro.setor = setor
        registro.respondido_em = timezone.now()

        registro.save(
            update_fields=[
                "responsavel",
                "setor",
                "respondido_em",
            ]
        )

        return render(
            request,
            "main/pages/confirm.html",
            {
                "registro": registro,
                "sucesso": True,
            },
        )

    return render(
        request,
        "main/pages/confirm.html",
        {
            "registro": registro,
        },
    )

