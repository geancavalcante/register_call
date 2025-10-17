from django import template

register = template.Library()

@register.filter(name='format_horas')
def format_horas(valor):
    """
    Converte horas em float para formato legível (Xh Ymin)
    Exemplo: 2.63 -> "2h 38min"
    """
    if valor is None or valor == 0:
        return '-'
    
    try:
        # Converter para float se for string
        if isinstance(valor, str):
            valor = float(valor)
        
        # Calcular horas e minutos
        horas = int(valor)
        minutos = int((valor - horas) * 60)
        
        # Formatar saída
        if horas > 0 and minutos > 0:
            return f"{horas}h {minutos}min"
        elif horas > 0:
            return f"{horas}h"
        elif minutos > 0:
            return f"{minutos}min"
        else:
            return '-'
    except (ValueError, TypeError):
        return '-'

