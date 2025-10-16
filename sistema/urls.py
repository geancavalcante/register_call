from django.urls import path
from . import views

urlpatterns = [
    path("", views.RegistrarChamado.as_view(), name="cadastrar_chamado"),
    path("salvar_dados_iniciais/", views.salvar_dados_iniciais, name="salvar_dados_iniciais"),
    path("dashboards/", views.dashboards, name="dashboards"),
    path("analistas/", views.nomes_analistas, name="nomes_analistas"),
    path("todos_chamados/", views.todos_chamados, name="todos_chamados"),
    path("tabela_chamados/", views.tabela_chamados, name="tabela_chamados"),
    path("exportar_excel_formatado/", views.exportar_excel_formatado, name="exportar_excel_formatado"),
    path("upload_planilha/", views.upload_planilha, name="upload_planilha"),
    path("finalizar_chamado/", views.finalizar_chamado, name="finalizar_chamado"),
    path("ver_analista/<int:user_id>/", views.ver_analista, name="ver_analista"),
    path("views/", views.views, name="views"),
    
]