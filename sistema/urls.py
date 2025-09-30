from django.urls import path
from . import views

urlpatterns = [
    path("", views.RegistrarChamado.as_view(), name="cadastrar_chamado"),
    path("ver_analista/<int:user_id>/", views.ver_analista, name="ver_analista"),
    path("views/", views.views, name="views"),
]