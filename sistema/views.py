from django.views import View
from django.shortcuts import render, redirect
from .models import Chamados
from django.contrib.auth.models import User
from datetime import datetime, date
from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from io import BytesIO


def dashboards(request):
    chamados = Chamados.objects.all()
    return render(request, "dashboards.html", {"chamados": chamados})

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
    chamados  = Chamados.objects.all()
    quantidade = chamados.count()


    return render(request, "todos_chamados.html", {"chamados": chamados, "quantidade": quantidade})


def dashboards(request):
    """
    Página de dashboards com gráficos e estatísticas
    """
    chamados = Chamados.objects.all()
    
    return render(request, "dashboards.html", {"chamados": chamados})


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
        if self.situacao == "produtiva":
            self.situacao = True
        else:
            self.situacao = False
   
        
    def _cauculo_de_tempo_de_atendimento(self):
        formato = "%H:%M"

        inicio = datetime.strptime(self.inicio, formato)
        conclusao = datetime.strptime(self.conclusao, formato)
        self.total_horas = str(conclusao - inicio)
    

    def _salvador_chamado(self):
            print(self.tipo_atividade)

            Chamados.objects.create(
                nome_analista = User.objects.get(username=self.nome_analista),
                ID_chamado = self.ID_chamado,
                tipo_atividade = self.tipo_atividade,
                nome_tecnico = self.nome_tecnico,
                data = self.data,
                inicio =  self.inicio,
                conclusao = self.conclusao,
                total_horas = self.total_horas,
                produtiva = self.situacao,
                senha = self.senha,
                observacao = self.observacao,
            )


# ==================== EXPORTAÇÃO DE RELATÓRIOS PDF ====================

def exportar_relatorio_pdf(request):
    """
    Exporta relatório de chamados em PDF
    Aceita parâmetros: data_inicio, data_fim, analista_id
    """
    # Obter parâmetros da requisição
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    analista_id = request.GET.get('analista_id')
    
    # Filtrar chamados
    chamados = Chamados.objects.all()
    
    if data_inicio:
        data_inicio_obj = datetime.strptime(data_inicio, '%Y-%m-%d').date()
        chamados = chamados.filter(data__gte=data_inicio_obj)
    
    if data_fim:
        data_fim_obj = datetime.strptime(data_fim, '%Y-%m-%d').date()
        chamados = chamados.filter(data__lte=data_fim_obj)
    
    if analista_id:
        chamados = chamados.filter(nome_analista_id=analista_id)
    
    # Criar o PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)
    
    # Container para os elementos
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#F8C24A'),
        spaceAfter=30,
        alignment=TA_CENTER,
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#1a1a2e'),
        spaceAfter=12,
        alignment=TA_CENTER,
    )
    
    # Título
    title = Paragraph("Relatório de Chamados - Attend Services", title_style)
    elements.append(title)
    
    # Informações do relatório
    periodo = f"Período: {data_inicio or 'Início'} até {data_fim or 'Hoje'}"
    periodo_p = Paragraph(periodo, subtitle_style)
    elements.append(periodo_p)
    elements.append(Spacer(1, 20))
    
    # Estatísticas resumidas
    total_chamados = chamados.count()
    produtivas = chamados.filter(produtiva=True).count()
    produtividade_pct = round((produtivas / total_chamados * 100)) if total_chamados > 0 else 0
    
    stats_data = [
        ['Métrica', 'Valor'],
        ['Total de Chamados', str(total_chamados)],
        ['Chamados Produtivos', str(produtivas)],
        ['Taxa de Produtividade', f'{produtividade_pct}%'],
        ['Analistas Ativos', str(chamados.values('nome_analista').distinct().count())],
    ]
    
    stats_table = Table(stats_data, colWidths=[3*inch, 2*inch])
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F8C24A')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1a1a2e')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
    ]))
    
    elements.append(stats_table)
    elements.append(Spacer(1, 30))
    
    # Título da tabela de chamados
    chamados_title = Paragraph("Detalhes dos Chamados", subtitle_style)
    elements.append(chamados_title)
    elements.append(Spacer(1, 12))
    
    # Tabela de chamados (limitada a 100 para não quebrar o PDF)
    data = [['ID', 'Analista', 'Tipo', 'Data', 'Tempo', 'Status']]
    
    for chamado in chamados[:100]:  # Limitar a 100 chamados
        analista = str(chamado.nome_analista).replace('_', ' ')
        status = '✓ Prod.' if chamado.produtiva else '✗ Improd.'
        data.append([
            str(chamado.ID_chamado),
            analista[:15],  # Limitar tamanho do nome
            chamado.tipo_atividade[:12],  # Limitar tamanho
            str(chamado.data),
            chamado.total_horas,
            status
        ])
    
    table = Table(data, colWidths=[0.8*inch, 1.5*inch, 1.3*inch, 1*inch, 0.8*inch, 0.9*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F8C24A')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1a1a2e')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.whitesmoke]),
    ]))
    
    elements.append(table)
    
    # Rodapé
    elements.append(Spacer(1, 30))
    footer = Paragraph(
        f"Relatório gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')} - Attend Services",
        styles['Normal']
    )
    elements.append(footer)
    
    # Construir PDF
    doc.build(elements)
    
    # Obter o valor do buffer e retornar
    pdf = buffer.getvalue()
    buffer.close()
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="relatorio_chamados_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf"'
    response.write(pdf)
    
    return response
