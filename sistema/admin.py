from django.contrib import admin

from .models import Chamados, Chamados_planejados, Chamados_andamentos

admin.site.register(Chamados)
admin.site.register(Chamados_planejados)
admin.site.register(Chamados_andamentos)
