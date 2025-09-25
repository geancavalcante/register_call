from django.http import HttpResponse
from django.shortcuts import render, redirect
from .models import Chamados

from datetime import date




def views(request):

    data = date.today()
    print(data)

    quantidade = Chamados.objects.filter(data=data).count()
    chamados  = Chamados.objects.all()
    return render(request, "visualização.html",  {"chamados": chamados, "quantidade": quantidade,"data":data})



def index(request):
    
    if request.method == "POST":
        #======================================

        produtiva_valor = request.POST.get("produtiva")
        if produtiva_valor == "on":
            produtiva_valor = True
        else:
            produtiva_valor = False

        #========================================
    
        inicio = request.POST.get("inicio")
        conclusao = request.POST.get("conclusao")
        print(inicio)
    

        inicio = float(inicio.replace(":", "."))
        conclusao = float(conclusao.replace(":", "."))

        
        #round: Arrendodar o valor para 2 casas decimais
        #abs: definiir o valor como positivo
    
        total_horas = round(abs(inicio - conclusao), 2) 
        total_horas = f"{float(total_horas):05.2f}".replace(".",":")
        print(total_horas)
        
    

        #==============================================
    
    

        Chamados.objects.create(
            nome_analista = request.POST.get("nome_analista"),
            ID_chamado = request.POST.get("ID_chamado"),
            tecnico = request.POST.get("tecnico"),
            data = request.POST.get("data"),
            inicio =  request.POST.get("inicio"),
            conclusao = request.POST.get("conclusao"),
            total_horas = total_horas,
            produtiva = produtiva_valor,
            senha = request.POST.get("senha"),
            observacao = request.POST.get("observacao")
        )

        

        return render(request, "index.html")

    
    else:
        return render(request, "index.html")


      
   

    
        
      
        

