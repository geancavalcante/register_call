from django.db import models
from datetime import datetime
from django.contrib.auth.models import User

class Chamados_planejados(models.Model):
    chamados_hoje = models.IntegerField()
    data = models.DateField(default=datetime.today)

    def __str__(self):
        return f"{self.data}"


class Chamados(models.Model):
    STATUS_CHOICES = [
        ('planejado', 'Planejado'),
        ('em_andamento', 'Em Andamento'),
        ('finalizado', 'Finalizado'),
        ('produtiva', 'Produtiva'),
        ('improdutiva', 'Improdutiva'),
    ]

    nome_analista = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    ID_chamado = models.CharField(max_length=50, unique=True)
    tipo_atividade = models.CharField(max_length=30, blank=True)
    nome_tecnico = models.CharField(max_length=30, blank=True)
    nome_cliente = models.CharField(max_length=100, blank=True)  # Novo campo para cliente
    data = models.DateField(default=datetime.today)
    data_planejada = models.DateField(null=True, blank=True)  # Data planejada da planilha
    inicio = models.TimeField(null=True, blank=True)
    conclusao = models.TimeField(null=True, blank=True)
    total_horas = models.TimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planejado')
    produtiva = models.BooleanField(default=True)
    senha = models.CharField(max_length=12, blank=True)
    observacao = models.TextField(blank=True)
    origem_planilha = models.BooleanField(default=False)  # Indica se veio de upload
    data_upload = models.DateTimeField(null=True, blank=True)  # Quando foi feito o upload

    def __str__(self):
        return f"Chamado {self.ID_chamado} - {self.get_status_display()}" 


