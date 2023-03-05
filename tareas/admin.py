from django.contrib import admin
from .models import *

# Register your models here.
class RecursoAdmin(admin.ModelAdmin):
    list_display = ('id', 'titulo',)

class CursoAsignaturaAdmin(admin.ModelAdmin):
    list_display = ('id', 'curso','profesor')

class CursoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre','paralelo')

class PersonaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombres','apellido1')

class AsignaturaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')

class TaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'title')

admin.site.register(Recurso, RecursoAdmin)
admin.site.register(CursoAsignatura, CursoAsignaturaAdmin)
admin.site.register(Curso, CursoAdmin)
admin.site.register(Persona, PersonaAdmin)
admin.site.register(Asignatura, AsignaturaAdmin)
admin.site.register(Task, TaskAdmin)