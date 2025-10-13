from django.views import View
from django.shortcuts import render, redirect
from .models import Chamados
from django.contrib.auth.models import User
from datetime import datetime, date, timedelta
from django.http import HttpResponse
from django.utils import timezone
from datetime import datetime, date



def dashboards(request):
    """
    View de dashboards - todos os filtros são aplicados no frontend.
    """
    # Buscar todos os chamados ordenados por data (mais recentes primeiro)
    chamados = Chamados.objects.all().order_by('-data', '-id')
    
    return render(request, "dashboards.html", {
        "chamados": chamados
    })

def nomes_analistas(request):
    analistas_str = []
    analistas_object = User.objects.filter(is_superuser=False)
   
   
    for analista in analistas_object:
        nome_analista = User.objects.get(username=analista)

        analista = str(analista).replace("_"," ")
        analistas_str.append((analista,nome_analista.id))
    


    return render(request, "analistas.html", {"analistas": analistas_str })

def ver_analista(request, user_id):
    hora = datetime.strptime("01:00","%H:%M").time()


    analista = User.objects.get(id=user_id)
    chamados_feitos = Chamados.objects.filter(nome_analista=analista)
    analista = str(analista).replace("_", " ")

    return render(request, "chamado_especifico.html" , {"chamados": chamados_feitos, "analista": analista, "hora": hora} )


def todos_chamados(request):
    """
    View para exibir todos os chamados com suporte a filtros.
    Usa date.today() para obter a data atual do sistema.
    """
    # Obter data atual usando date.today()
    hoje = date.today()
    
    # Buscar todos os chamados ordenados por data (mais recentes primeiro)
    chamados = Chamados.objects.all().order_by('-data', '-id')
    quantidade = chamados.count()
    
    # Filtros opcionais via GET parameters (para uso futuro)
    filtro_periodo = request.GET.get('period', None)
    
    if filtro_periodo == 'today':
        # Filtrar apenas chamados de hoje
        chamados = Chamados.objects.filter(data=hoje).order_by('-id')
        quantidade = chamados.count()
        print(f"🗓️ Filtro HOJE aplicado (todos_chamados): {hoje} - {quantidade} chamados")
    
    elif filtro_periodo == '7':
        # Últimos 7 dias
        data_limite = hoje - timedelta(days=7)
        chamados = Chamados.objects.filter(data__gte=data_limite).order_by('-data', '-id')
        quantidade = chamados.count()
    
    elif filtro_periodo == '30':
        # Últimos 30 dias
        data_limite = hoje - timedelta(days=30)
        chamados = Chamados.objects.filter(data__gte=data_limite).order_by('-data', '-id')
        quantidade = chamados.count()

    return render(request, "todos_chamados.html", {
        "chamados": chamados, 
        "quantidade": quantidade,
        "data_hoje": hoje  # Enviar data atual para o template
    })




def views(request):
    

    if request.method == "POST":

        formato = "%Y-%m-%d"
        data_especifica = request.POST.get("data") 
        data_especifica = datetime.strptime(data_especifica, formato).date()
        data_hoje = date.today()



        hora = datetime.strptime("01:00","%H:%M").time()

        

        chamados = Chamados.objects.filter(data=data_especifica) 
        quantidade = Chamados.objects.filter(data=data_especifica).count() 

        return render(request, "visualização.html", {"chamados":chamados, "quantidade": quantidade, "data_especificada":data_especifica,"data_hoje": data_hoje, "hora":hora}  )
    else:


        hora = datetime.strptime("01:00", "%H:%M").time()
        data_especifica = date.today()
        data_hoje = date.today()



        quantidade = Chamados.objects.filter(data=data_especifica).count()
        chamados  = Chamados.objects.all()
        return render(request, "visualização.html",  {"chamados":chamados, "quantidade": quantidade,"data_especificada":data_especifica,"data_hoje":data_hoje, "hora":hora})



class RegistrarChamado(View):

    def get(self, request):
        return render(request, "index.html")
    

    def post(self, request):
        self.nome_analista = request.POST.get("nome_analista")
        self.ID_chamado = request.POST.get("ID_chamado")
        self.tipo_atividade = request.POST.get("tipo_atividade")
        self.nome_tecnico = request.POST.get("tecnico")
        self.data = request.POST.get("data")
        self.inicio =  request.POST.get("inicio")
        self.conclusao = request.POST.get("conclusao")
        self.situacao = request.POST.get("produtiva")
        self.senha = request.POST.get("senha")
        self.observacao = request.POST.get("observacao")



    
        RegistrarChamado._validar_situacao(self)
        RegistrarChamado._cauculo_de_tempo_de_atendimento(self)
        RegistrarChamado._salvador_chamado(self)
            
        return render(request, "index.html")

    


    def _validar_situacao(self):
        if self.situacao == "on":

            self.situacao = True
        
        else:
            self.situacao = False
   
        
    def _cauculo_de_tempo_de_atendimento(self):
        formato = "%H:%M"

        inicio = datetime.strptime(self.inicio, formato)
        conclusao = datetime.strptime(self.conclusao, formato)
        self.total_horas = str(conclusao - inicio)
    

    def _salvador_inicio_chamado(self):

            Chamados.objects.create(
                nome_analista = User.objects.get(username=self.nome_analista),
                ID_chamado = self.ID_chamado,
                tipo_atividade = self.tipo_atividade,
                nome_tecnico = self.nome_tecnico,
                data = self.data,
                inicio =  self.inicio,
            )

    def _salvar_conclusao_chamado(self):

        Chamados.objects.create(
        conclusao = self.conclusao,
        total_horas = self.total_horas,
        produtiva = self.situacao,
        senha = self.senha,
        observacao = self.observacao,)

        #filtrar o chamado que ta la e mudar os esses campos, 



