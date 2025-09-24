from django.http import HttpResponse
from django.shortcuts import render, redirect
from .models import Informations




def views(request):
    quantidade = Informations.objects.count()
    chamados  = Informations.objects.all()
    return render(request, "visualização.html",  {"chamados": chamados, "quantidade": quantidade})



def index(request):

    if request.method == "POST":
        Informations.objects.create(
            nome_analista = request.POST.get("nome_analista"),
            inc_chamado = request.POST.get("inc_chamado"),
            senha = request.POST.get("senha"),
        )

        return render(request, "index.html")

    
    else:
        return render(request, "index.html")


      
   

    
        
      
        

