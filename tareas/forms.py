from django import forms
from django.utils.safestring import mark_safe
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.forms.widgets import DateTimeBaseInput

class CustomDateInput(DateTimeBaseInput):
    def format_value(self, value):
        return str(value or '')

class Base(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.ver = kwargs.pop('ver') if 'ver' in kwargs else False
        self.editando = 'instance' in kwargs
        no_requeridos = kwargs.pop('no_requeridos') if 'no_requeridos' in kwargs else []
        requeridos = kwargs.pop('requeridos') if 'requeridos' in kwargs else []
        if self.editando:
            self.instancia = kwargs['instance']
        super(Base, self).__init__(*args, **kwargs)
        for nr in no_requeridos:
            self.fields[nr].required = False
        for r in requeridos:
            self.fields[r].required = True
        for k, v in self.fields.items():
            field = self.fields[k]
            if isinstance(field, forms.TimeField):
                attrs_ = self.fields[k].widget.attrs
                self.fields[k].widget = CustomDateInput(attrs={'type': 'time'})
                self.fields[k].widget.attrs = attrs_
            if isinstance(field, forms.DateField):
                attrs_ = self.fields[k].widget.attrs
                self.fields[k].widget = CustomDateInput(attrs={'type': 'date'})
                self.fields[k].widget.attrs = attrs_
                self.fields[k].widget.attrs['class'] = "form-control"
                # self.fields[k].input_formats = ['%d/%m/%Y']
            elif isinstance(field, forms.BooleanField):
                if 'data-switchery' in self.fields[k].widget.attrs and eval(self.fields[k].widget.attrs['data-switchery'].capitalize()):
                    if 'class' in self.fields[k].widget.attrs :
                        self.fields[k].widget.attrs['class'] += " js-switch"
                    else:
                        self.fields[k].widget.attrs['class'] = "js-switch"
            else:
                if 'class' in self.fields[k].widget.attrs:
                    self.fields[k].widget.attrs['class'] += "form-control"
                else:
                    self.fields[k].widget.attrs['class'] = "form-control"
            if not 'col' in self.fields[k].widget.attrs:
                self.fields[k].widget.attrs['col'] = "12"
            if self.fields[k].required and self.fields[k].label:
                self.fields[k].label = mark_safe(self.fields[k].label + '<span style="color:rgb(30, 144, 255);margin-left:2px;"><strong>*</strong></span>')
            self.fields[k].widget.attrs['data-nameinput'] = k
            if self.ver:
                self.fields[k].widget.attrs['readonly'] = "readonly"

class LoginForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ["username", "password"]

    def clean_username(self):
        #username must be unique.
        username=self.cleaned_data['username'].lower()
        return username
    
class PersonaForm(Base):
    perfil = forms.ChoiceField(choices=PERFIL_USUARIO[:3])
    class Meta:
        model=Persona
        fields=[
            "cedula",
            "nombres",
            "apellido1",
            "apellido2",
            "correo",
            "genero",
            "perfil",
            "fecha_nacimiento",
            "telefono",
            "direccion",
            "ciudad",
            "picture",
            ]
        widgets = {
            'genero': forms.Select(attrs={'class': 'form-control'}),
            'perfil': forms.Select(attrs={'class': 'form-control'})
            }

class CursoAsignaturaForm(Base):
    
    class Meta:
        model=CursoAsignatura
        fields=[
            "asignatura",
            "profesor",
            ]
        widgets = {
            'asignatura': forms.Select(attrs={'class': 'form-control'}),
            'profesor': forms.Select(attrs={'class': 'form-control'}),
            }

class CursoForm(Base):
    class Meta:
        model=Curso
        fields=[
            "nombre",
            "paralelo",
            "descripcion",
            "estudiantes",
            ]
        widgets = {
            # 'curso': forms.Select(attrs={'class': 'form-control'}),
            # 'asignatura': forms.Select(attrs={'class': 'form-control'}),
            # 'profesor': forms.Select(attrs={'class': 'form-control'}),
            'estudiantes': forms.SelectMultiple(attrs={'class': 'form-control'}),
            }
class TaskForm(Base):
    class Meta:
        model = Task
        fields = [
            "title",
            "recursos",
            "description",
            "archivo",
        ]
        widgets = {
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'recursos': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }


class RecursoForm(Base):
    class Meta:
        model = Recurso
        fields = [
            "titulo",
            "descripcion",
            "enlace",
            "archivo",
        ]
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.TextInput(attrs={'class': 'form-control'}),
            'enlace': forms.TextInput(attrs={'class': 'form-control no_requeridos'}),
            'archivo': forms.FileInput(attrs={'class': 'form-control no_requeridos'}),
        }