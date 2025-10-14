from django.views import View
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from datetime import datetime, timedelta
import json
import pandas as pd
import os
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from .models import Chamados

# View para página inicial (registrar chamado)
@method_decorator(login_required, name='dispatch')
class RegistrarChamado(View):
    def get(self, request):
        # Verificar se há um chamado em andamento para o usuário atual
        chamado_em_andamento = None
        if request.user.is_authenticated:
            chamado_em_andamento = Chamados.objects.filter(
                nome_analista=request.user,
                status='em_andamento'
            ).first()
        
        context = {
            'chamado_em_andamento': chamado_em_andamento
        }
        return render(request, "index.html", context)

    def post(self, request):
        try:
            # Coletar dados do formulário
            nome_analista = request.POST.get("nome_analista")
            ID_chamado = request.POST.get("ID_chamado")
            tipo_atividade = request.POST.get("tipo_atividade")
            nome_tecnico = request.POST.get("tecnico")
            data = request.POST.get("data")
            inicio = request.POST.get("inicio")
            conclusao = request.POST.get("conclusao")
            situacao = request.POST.get("produtiva")
            senha = request.POST.get("senha")
            observacao = request.POST.get("observacao")

            # Validar dados obrigatórios
            if not all([nome_analista, ID_chamado, tipo_atividade, 
                       nome_tecnico, data, inicio, conclusao, 
                       senha]):
                messages.error(request, "Todos os campos obrigatórios devem ser preenchidos.")
                return render(request, "index.html")

            # Verificar se o analista existe
            try:
                analista = User.objects.get(username=nome_analista)
            except User.DoesNotExist:
                messages.error(request, "Analista não encontrado.")
                return render(request, "index.html")

            # Verificar se o chamado já existe
            chamado_existente = Chamados.objects.filter(ID_chamado=ID_chamado).first()
            
            if chamado_existente:
                # Se o chamado existe e está planejado, atualizar para em_andamento
                if chamado_existente.status == 'planejado':
                    chamado_existente.status = 'em_andamento'
                    chamado_existente.nome_analista = analista
                    chamado_existente.tipo_atividade = tipo_atividade
                    chamado_existente.nome_tecnico = nome_tecnico
                    chamado_existente.data = data
                    chamado_existente.inicio = inicio
                    chamado_existente.conclusao = conclusao
                    chamado_existente.produtiva = situacao == 'true'
                    chamado_existente.senha = senha
                    chamado_existente.observacao = observacao
                    chamado_existente.save()
                    messages.success(request, "Chamado atualizado de 'Planejado' para 'Em Andamento' com sucesso!")
                # Se o chamado existe e está em_andamento, atualizar para finalizado
                elif chamado_existente.status == 'em_andamento':
                    # Atualizar todos os campos
                    chamado_existente.nome_analista = analista
                    chamado_existente.tipo_atividade = tipo_atividade
                    chamado_existente.nome_tecnico = nome_tecnico
                    chamado_existente.data = data
                    chamado_existente.inicio = inicio
                    chamado_existente.conclusao = conclusao
                    chamado_existente.produtiva = situacao == 'true'
                    chamado_existente.senha = senha
                    chamado_existente.observacao = observacao
                    
                    # Se veio de planilha, manter status finalizado
                    # Se foi criado manualmente, usar status baseado em produtiva
                    if chamado_existente.origem_planilha:
                        chamado_existente.status = 'finalizado'
                    else:
                        # Para chamados criados manualmente, usar status baseado em produtiva
                        chamado_existente.status = 'produtiva' if situacao == 'true' else 'improdutiva'
                    
                    chamado_existente.save()
                    messages.success(request, "Chamado finalizado com sucesso!")
                else:
                    messages.error(request, f"Chamado já existe com status: {chamado_existente.get_status_display()}")
                    return render(request, "index.html")
            else:
                # Criar novo chamado
                chamado = Chamados.objects.create(
                    ID_chamado=ID_chamado,
                    nome_analista=analista,
                    tipo_atividade=tipo_atividade,
                    nome_tecnico=nome_tecnico,
                    data=data,
                    inicio=inicio,
                    conclusao=conclusao,
                    produtiva=situacao == 'true',
                    senha=senha,
                    observacao=observacao,
                    origem_planilha=False
                )
                messages.success(request, "Chamado registrado com sucesso!")

            return redirect('registrar_chamado')

        except Exception as e:
            messages.error(request, f"Erro ao processar o chamado: {str(e)}")
            return render(request, "index.html")

# View para salvar dados iniciais via AJAX
@csrf_exempt
@require_http_methods(["POST"])
def salvar_dados_iniciais(request):
    """
    View para salvar dados iniciais do chamado via AJAX
    """
    try:
        data = json.loads(request.body)
        
        # Validar campos obrigatórios
        campos_obrigatorios = ['ID_chamado', 'nome_analista', 'tipo_atividade', 'tecnico', 'data', 'inicio']
        for campo in campos_obrigatorios:
            if not data.get(campo):
                return JsonResponse({
                    'success': False,
                    'message': f'Campo {campo} é obrigatório'
                }, status=400)
        
        # Verificar se o analista existe
        try:
            analista = User.objects.get(username=data['nome_analista'])
        except User.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Analista não encontrado'
            }, status=400)
        
        # Verificar se o ID do chamado já existe
        chamado_existente = Chamados.objects.filter(ID_chamado=data['ID_chamado']).first()
        if chamado_existente:
            # Se o chamado existe e está planejado, atualizar para em_andamento
            if chamado_existente.status == 'planejado':
                # Atualizar o chamado planejado para em_andamento
                chamado_existente.status = 'em_andamento'
                chamado_existente.nome_analista = analista
                chamado_existente.tipo_atividade = data['tipo_atividade']
                chamado_existente.nome_tecnico = data['tecnico']
                chamado_existente.data = datetime.strptime(data['data'], '%Y-%m-%d').date()
                chamado_existente.inicio = datetime.strptime(data['inicio'], '%H:%M').time()
                chamado_existente.save()
                
                return JsonResponse({
                    'success': True,
                    'message': 'Chamado planejado encontrado e atualizado para "Em Andamento"! Pode continuar com o preenchimento.',
                    'chamado_existente': True,
                    'status_atual': 'em_andamento',
                    'chamado_id': chamado_existente.ID_chamado
                })
            elif chamado_existente.status == 'em_andamento':
                return JsonResponse({
                    'success': True,
                    'message': 'Chamado em andamento encontrado. Pode finalizar o chamado.',
                    'chamado_existente': True,
                    'status_atual': 'em_andamento'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': f'Chamado já existe com status: {chamado_existente.get_status_display()}'
                }, status=400)
        
        # Validar formato de data
        try:
            datetime.strptime(data['data'], '%Y-%m-%d')
        except ValueError:
            return JsonResponse({
                'success': False,
                'message': 'Formato de data inválido. Use YYYY-MM-DD'
            }, status=400)
        
        # Validar formato de hora
        try:
            datetime.strptime(data['inicio'], '%H:%M')
        except ValueError:
            return JsonResponse({
                'success': False,
                'message': 'Formato de hora inválido. Use HH:MM'
            }, status=400)
        
        return JsonResponse({
            'success': True,
            'message': 'Dados válidos. Pode continuar com o preenchimento.'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Dados JSON inválidos'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }, status=500)

# View para dashboard
@login_required
def dashboard(request):
    # Obter filtros da URL
    periodo = request.GET.get('periodo', 'hoje')
    analista = request.GET.get('analista', '')
    tipo_atividade = request.GET.get('tipo_atividade', '')
    produtividade = request.GET.get('produtividade', '')
    
    # Construir query base
    chamados = Chamados.objects.all()
    
    # Aplicar filtros
    if periodo == 'hoje':
        hoje = timezone.now().date()
        chamados = chamados.filter(data=hoje)
    elif periodo == 'semana':
        inicio_semana = timezone.now().date() - timedelta(days=7)
        chamados = chamados.filter(data__gte=inicio_semana)
    elif periodo == 'mes':
        inicio_mes = timezone.now().date() - timedelta(days=30)
        chamados = chamados.filter(data__gte=inicio_mes)
    
    if analista:
        chamados = chamados.filter(nome_analista__username=analista)
    
    if tipo_atividade:
        chamados = chamados.filter(tipo_atividade=tipo_atividade)
    
    if produtividade == 'produtiva':
        chamados = chamados.filter(produtiva=True)
    elif produtividade == 'improdutiva':
        chamados = chamados.filter(produtiva=False)
    
    # Calcular estatísticas
    total_chamados = chamados.count()
    chamados_produtivos = chamados.filter(produtiva=True).count()
    chamados_improdutivos = chamados.filter(produtiva=False).count()
    chamados_planejados = chamados.filter(status='planejado').count()
    chamados_em_andamento = chamados.filter(status='em_andamento').count()
    chamados_finalizados = chamados.filter(status='finalizado').count()
    
    # Calcular taxa de produtividade
    if total_chamados > 0:
        taxa_produtividade = (chamados_produtivos / total_chamados) * 100
    else:
        taxa_produtividade = 0
    
    # Obter dados para filtros
    analistas = User.objects.filter(chamados__isnull=False).distinct()
    tipos_atividade = Chamados.objects.values_list('tipo_atividade', flat=True).distinct()
    
    context = {
        'chamados': chamados,  # Adicionar os chamados para o template
        'total_chamados': total_chamados,
        'chamados_produtivos': chamados_produtivos,
        'chamados_improdutivos': chamados_improdutivos,
        'chamados_planejados': chamados_planejados,
        'chamados_em_andamento': chamados_em_andamento,
        'chamados_finalizados': chamados_finalizados,
        'taxa_produtividade': round(taxa_produtividade, 2),
        'analistas': analistas,
        'tipos_atividade': tipos_atividade,
        'filtros': {
            'periodo': periodo,
            'analista': analista,
            'tipo_atividade': tipo_atividade,
            'produtividade': produtividade
        }
    }
    
    return render(request, 'dashboards.html', context)

# View para todos os chamados
@login_required
def todos_chamados(request):
    chamados = Chamados.objects.all().order_by('-data', '-inicio')
    
    # Paginação
    paginator = Paginator(chamados, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'chamados': page_obj,
        'total_chamados': chamados.count()
    }
    
    return render(request, 'todos_chamados.html', context)

# View para tabela dinâmica
@login_required
def tabela_chamados(request):
    # Obter filtros da URL
    periodo = request.GET.get('periodo', '')
    analista = request.GET.get('analista', '')
    tipo_atividade = request.GET.get('tipo_atividade', '')
    produtividade = request.GET.get('produtividade', '')
    status = request.GET.get('status', '')
    
    # Construir query base
    chamados = Chamados.objects.all().order_by('-data', '-inicio')
    
    # Aplicar filtros
    if periodo == 'hoje':
        hoje = timezone.now().date()
        chamados = chamados.filter(data=hoje)
    elif periodo == 'semana':
        inicio_semana = timezone.now().date() - timedelta(days=7)
        chamados = chamados.filter(data__gte=inicio_semana)
    elif periodo == 'mes':
        inicio_mes = timezone.now().date() - timedelta(days=30)
        chamados = chamados.filter(data__gte=inicio_mes)
    
    if analista:
        chamados = chamados.filter(nome_analista__username=analista)
    
    if tipo_atividade:
        chamados = chamados.filter(tipo_atividade=tipo_atividade)
    
    if produtividade == 'produtiva':
        chamados = chamados.filter(produtiva=True)
    elif produtividade == 'improdutiva':
        chamados = chamados.filter(produtiva=False)
    
    if status:
        chamados = chamados.filter(status=status)
    
    context = {
        'chamados': chamados,
        'filtros': {
            'periodo': periodo,
            'analista': analista,
            'tipo_atividade': tipo_atividade,
            'produtividade': produtividade,
            'status': status
        }
    }
    
    return render(request, 'tabela_chamados.html', context)

# View para upload de planilha
@login_required
def upload_planilha(request):
    if request.method == 'POST':
        try:
            arquivo = request.FILES.get('arquivo')
            if not arquivo:
                return JsonResponse({
                    'success': False,
                    'message': 'Nenhum arquivo foi enviado'
                }, status=400)
            
            # Verificar extensão do arquivo
            if not arquivo.name.endswith(('.xlsx', '.xls', '.csv')):
                return JsonResponse({
                    'success': False,
                    'message': 'Formato de arquivo não suportado. Use .xlsx, .xls ou .csv'
                }, status=400)
            
            # Ler arquivo
            if arquivo.name.endswith('.csv'):
                df = pd.read_csv(arquivo, encoding='utf-8')
            else:
                df = pd.read_excel(arquivo)
            
            # Verificar colunas obrigatórias
            colunas_obrigatorias = ['ICKET', 'Ponto', 'Cidade', 'UF', 'TÉCNICO', 'NÚMERO', 'DATA', 'SERVIÇO']
            colunas_faltando = [col for col in colunas_obrigatorias if col not in df.columns]
            
            if colunas_faltando:
                return JsonResponse({
                    'success': False,
                    'message': f'Colunas obrigatórias faltando: {", ".join(colunas_faltando)}'
                }, status=400)
            
            # Processar dados
            chamados_criados = 0
            for index, row in df.iterrows():
                try:
                    # Extrair ID do chamado (remover prefixo se existir)
                    id_chamado = str(row['ICKET']).strip()
                    if id_chamado.startswith('ICKET'):
                        id_chamado = id_chamado[5:].strip()
                    
                    # Verificar se já existe
                    if Chamados.objects.filter(ID_chamado=id_chamado).exists():
                        continue
                    
                    # Converter data
                    data_planejada = pd.to_datetime(row['DATA']).date()
                    
                    # Criar observação com informações adicionais
                    observacao = f"Ponto: {row['Ponto']}\n"
                    observacao += f"Cidade: {row['Cidade']}\n"
                    observacao += f"UF: {row['UF']}\n"
                    observacao += f"Número: {row['NÚMERO']}\n"
                    observacao += f"Serviço: {row['SERVIÇO']}"
                    
                    # Criar chamado
                    Chamados.objects.create(
                        ID_chamado=id_chamado,
                        nome_tecnico=row['TÉCNICO'],
                        data=data_planejada,
                        observacao=observacao,
                        status='planejado',
                        origem_planilha=True
                    )
                    
                    chamados_criados += 1
                    
                except Exception as e:
                    print(f"Erro ao processar linha {index}: {str(e)}")
                    continue
            
            return JsonResponse({
                'success': True,
                'message': f'{chamados_criados} chamados planejados criados com sucesso!'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Erro ao processar arquivo: {str(e)}'
            }, status=500)
    
    return render(request, 'upload_planilha.html')

# View para exportar Excel formatado
@login_required
def exportar_excel_formatado(request):
    # Obter filtros da URL
    periodo = request.GET.get('periodo', '')
    analista = request.GET.get('analista', '')
    tipo_atividade = request.GET.get('tipo_atividade', '')
    produtividade = request.GET.get('produtividade', '')
    
    # Construir query base
    chamados = Chamados.objects.all().order_by('-data', '-inicio')
    
    # Aplicar filtros
    if periodo == 'hoje':
        hoje = timezone.now().date()
        chamados = chamados.filter(data=hoje)
    elif periodo == 'semana':
        inicio_semana = timezone.now().date() - timedelta(days=7)
        chamados = chamados.filter(data__gte=inicio_semana)
    elif periodo == 'mes':
        inicio_mes = timezone.now().date() - timedelta(days=30)
        chamados = chamados.filter(data__gte=inicio_mes)
    
    if analista:
        chamados = chamados.filter(nome_analista__username=analista)
    
    if tipo_atividade:
        chamados = chamados.filter(tipo_atividade=tipo_atividade)
    
    if produtividade == 'produtiva':
        chamados = chamados.filter(produtiva=True)
    elif produtividade == 'improdutiva':
        chamados = chamados.filter(produtiva=False)
    
    # Criar workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "Chamados"
    
    # Definir estilos
    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="2C3E50", end_color="2C3E50", fill_type="solid")
    border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )
    center_alignment = Alignment(horizontal='center', vertical='center')
    
    # Cabeçalhos
    headers = ['ID Chamado', 'Analista', 'Tipo Atividade', 'Técnico', 'Data', 'Início', 'Conclusão', 'Status', 'Observação']
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.border = border
        cell.alignment = center_alignment
    
    # Dados
    for row, chamado in enumerate(chamados, 2):
        # Determinar status
        if chamado.origem_planilha:
            if chamado.status == 'planejado':
                status = 'Planejado'
            elif chamado.status == 'em_andamento':
                status = 'Em Andamento'
            elif chamado.status == 'finalizado':
                status = 'Finalizado'
            else:
                status = 'Desconhecido'
        else:
            status = 'Produtiva' if chamado.produtiva else 'Improdutiva'
        
        data = [
            chamado.ID_chamado,
            chamado.nome_analista.username if chamado.nome_analista else '',
            chamado.tipo_atividade,
            chamado.nome_tecnico,
            chamado.data.strftime('%d/%m/%Y') if chamado.data else '',
            chamado.inicio,
            chamado.conclusao,
            status,
            chamado.observacao or ''
        ]
        
        for col, value in enumerate(data, 1):
            cell = ws.cell(row=row, column=col, value=value)
            cell.border = border
            if col in [5, 6, 7]:  # Data, Início, Conclusão
                cell.alignment = center_alignment
    
    # Ajustar largura das colunas
    for col in range(1, len(headers) + 1):
        column_letter = get_column_letter(col)
        ws.column_dimensions[column_letter].width = 15
    
    # Resposta
    from django.http import HttpResponse
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="chamados_formatados.xlsx"'
    
    wb.save(response)
    return response

# View para dashboards (alias para dashboard)
def dashboards(request):
    return dashboard(request)

# View para nomes de analistas
@login_required
def nomes_analistas(request):
    # Criar lista de tuplas (username, id) para cada analista
    analistas = [(user.username, user.id) for user in User.objects.all()]
    context = {'analistas': analistas}
    return render(request, 'analistas.html', context)

# View para ver analista específico
@login_required
def ver_analista(request, user_id):
    try:
        analista = User.objects.get(id=user_id)
        chamados = Chamados.objects.filter(nome_analista=analista).order_by('-data', '-inicio')
        
        # Paginação
        paginator = Paginator(chamados, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'analista': analista,
            'chamados': page_obj,
            'total_chamados': chamados.count()
        }
        return render(request, 'ver_analista.html', context)
    except User.DoesNotExist:
        messages.error(request, "Analista não encontrado.")
        return redirect('nomes_analistas')

# View genérica para views.html
def views(request):
    return render(request, 'views.html')