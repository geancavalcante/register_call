from django.urls import path
from . import views

urlpatterns = [
    path("", views.RegistrarChamado.as_view(), name="cadastrar_chamado"),
    path("analistas/", views.nomes_analistas, name="nomes_analistas"),
    path("todos_chamados/", views.todos_chamados, name="todos_chamados"),
    path("ver_analista/<int:user_id>/", views.ver_analista, name="ver_analista"),
    path("views/", views.views, name="views"),
    path("dashboards/", views.dashboards, name="dashboards"),
]