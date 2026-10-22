from django.urls import path
from . import views

app_name = "main"

urlpatterns = [
    path(
        "confirmar/<str:token>/",
        views.confirmar_email,
        name="confirmar_email",
    ),
]
