#!/usr/bin/env python
import os
import sys
import django
from datetime import date

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'source.settings')
django.setup()

from sistema.models import Chamados
from django.db import models

def debug_chamados():
    print("🔍 DIAGNÓSTICO DOS CHAMADOS")
    print("=" * 50)
    
    # Data atual
    hoje = date.today()
    print(f"📅 Data atual: {hoje}")
    
    # Total de chamados
    total_chamados = Chamados.objects.count()
    print(f"📊 Total de chamados no banco: {total_chamados}")
    
    # Chamados com origem_planilha = True
    chamados_planilha = Chamados.objects.filter(origem_planilha=True)
    print(f"📋 Chamados de planilha: {chamados_planilha.count()}")
    
    # Chamados que apareceriam com a lógica atual
    chamados_visiveis = Chamados.objects.filter(
        models.Q(data_planejada__lte=hoje) | models.Q(data_planejada__isnull=True)
    )
    print(f"👁️ Chamados visíveis (data_planejada <= hoje): {chamados_visiveis.count()}")
    
    # Chamados de planilha que apareceriam
    chamados_planilha_visiveis = chamados_planilha.filter(
        models.Q(data_planejada__lte=hoje) | models.Q(data_planejada__isnull=True)
    )
    print(f"📋 Chamados de planilha visíveis: {chamados_planilha_visiveis.count()}")
    
    # Detalhes dos chamados de planilha
    print("\n📋 DETALHES DOS CHAMADOS DE PLANILHA:")
    for chamado in chamados_planilha[:5]:  # Mostrar apenas os primeiros 5
        print(f"  • ID: {chamado.ID_chamado}")
        print(f"    Data: {chamado.data}")
        print(f"    Data Planejada: {chamado.data_planejada}")
        print(f"    Previsto: {chamado.previsto}")
        print(f"    Status: {chamado.status}")
        print(f"    Origem Planilha: {chamado.origem_planilha}")
        print(f"    Data Upload: {chamado.data_upload}")
        print("    ---")
    
    # Chamados que NÃO aparecem (data_planejada > hoje)
    chamados_ocultos = chamados_planilha.filter(data_planejada__gt=hoje)
    print(f"\n🚫 Chamados ocultos (data_planejada > hoje): {chamados_ocultos.count()}")
    
    if chamados_ocultos.exists():
        print("📋 CHAMADOS OCULTOS:")
        for chamado in chamados_ocultos[:3]:
            print(f"  • ID: {chamado.ID_chamado}")
            print(f"    Data Planejada: {chamado.data_planejada}")
            print(f"    Data Atual: {hoje}")
            print(f"    Diferença: {(chamado.data_planejada - hoje).days} dias")
            print("    ---")

if __name__ == "__main__":
    debug_chamados()
