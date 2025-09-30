from django.db import models
from datetime import datetime
from django.contrib.auth.models import User


class Chamados(models.Model):

    nome_analista = models.ForeignKey(User, on_delete=models.CASCADE)
    ID_chamado = models.IntegerField()
    tipo_atividade = models.CharField(max_length=30)
    nome_tecnico = models.CharField(max_length=30)
    data = models.DateField(default=datetime.today)
    inicio = models.TimeField()
    conclusao = models.TimeField()
    total_horas = models.TimeField()
    produtiva = models.BooleanField(default=True)
    senha = models.CharField(max_length=12)
    observacao = models.TextField()


    def __str__(self):
        return f"{self.nome_analista} || {self.data}  || {self.inicio}" 


    