from django.db import models

class Informations(models.Model):
    nome_analista = models.CharField(max_length=50)
    inc_chamado = models.IntegerField()
    senha = models.CharField(max_length=12)

    def __str__(self):
        return f"{self.nome_analista} || {self.inc_chamado}" 


    