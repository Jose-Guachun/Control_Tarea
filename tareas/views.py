from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.urls import reverse, reverse_lazy
from tareas.forms import * 
from django.conf import settings
from django.views.generic.edit import FormView
# Django decorators
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.db import transaction
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.db.models import Q
from django.template.loader import get_template

from .models import *
from .forms import TaskForm
from Tarea.funciones import MiPaginador, generar_nombre
def signup(request):
    if request.method == 'GET':
        return render(request, 'signup.html', {"form": UserCreationForm})
    else:
        try:
            form= UserCreationForm(request.POST)
            if form.is_valid():
                user = User.objects.create_user( request.POST["username"], password=request.POST["password1"])
                user.save()
                login(request, user)
                return redirect('login')
            else:
                return render(request, 'signup.html', {"form": form})
        except Exception as ex:
            return render(request, 'signup.html', {"form": UserCreationForm(request.POST),"error":str(ex)})

@login_required
def signout(request):
    logout(request)
    return redirect('login')

class LoginView(FormView):
    # login view
    template_name='signin.html'
    form_class= LoginForm
    success_url=reverse_lazy('home')

    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(self.get_success_url())
        else:
            return super(LoginView, self).dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        login(self.request, form.get_user())
        return super(LoginView, self).form_valid(form)      

@login_required
@transaction.atomic()
def cargarsistema(request):
    data={}
    usuario = request.user
    persona=Persona.objects.filter(user=usuario)
    if request.method == 'POST':
        action = request.POST['action']
        if action == 'addpersona':
            try:
                form = PersonaForm(request.POST)
                if form.is_valid():
                    if not Persona.objects.filter(user=request.user).exists():
                        instance = Persona(nombres=form.cleaned_data['nombres'],
                                        user=request.user,
                                        apellido1=form.cleaned_data['apellido1'],
                                        apellido2=form.cleaned_data['apellido2'],
                                        cedula=form.cleaned_data['cedula'],
                                        genero=form.cleaned_data['genero'],
                                        perfil=form.cleaned_data['perfil'],
                                        fecha_nacimiento=form.cleaned_data['fecha_nacimiento'],
                                        telefono=form.cleaned_data['telefono'],
                                        direccion=form.cleaned_data['direccion'],
                                        ciudad=form.cleaned_data['ciudad'],
                                        )
                        instance.save(request)
                        if 'picture' in request.FILES:
                            newfile = request.FILES['picture']
                            newfile._name =  generar_nombre(f'{request.user.username}', newfile._name)
                            instance.picture = newfile
                        instance.save(request)
                    else:
                        persona=Persona.objects.get(user=request.user)
                        persona.nombres=form.cleaned_data['nombres'],
                        persona.apellido1=form.cleaned_data['apellido1'],
                        persona.apellido2=form.cleaned_data['apellido2'],
                        persona.cedula=form.cleaned_data['cedula'],
                        persona.genero=form.cleaned_data['genero'],
                        persona.perfil=form.cleaned_data['perfil'],
                        persona.fecha_nacimiento=form.cleaned_data['fecha_nacimiento'],
                        persona.telefono=form.cleaned_data['telefono'],
                        persona.direccion=form.cleaned_data['direccion'],
                        persona.ciudad=form.cleaned_data['ciudad'],
                        if 'picture' in request.FILES:
                            newfile = request.FILES['picture']
                            newfile._name = generar_nombre(f'{request.user.username}', newfile._name)
                            persona.picture = newfile
                        persona.save(request)
                    return redirect('home')
                else:
                    return render(request, 'actualizarperfil.html',{"form": form})
            except Exception as ex:
                transaction.set_rollback(True)
                return render(request, 'actualizarperfil.html', {"error": "Error: {}".format(str(ex)),"form":PersonaForm(request.POST)})
        return JsonResponse({"result": "bad", "mensaje": u"Solicitud Incorrecta."})
    else:
        if not persona:
            template='actualizarperfil.html'
            return render(request, template,{"form": PersonaForm()})
        data['persona']=persona=Persona.objects.get(user=usuario)
        if 'action' in request.GET:
            data['action'] = action = request.GET['action']
            if action == 'cursos':
                data['title']='Cursos'
                search, filtro, url_vars = request.GET.get('s', ''), Q(status=True), ''
                if search:
                    filtro = filtro & Q(nombre__icontains=search)
                    url_vars += '&s=' + search
                    data['search'] = search
                listado = CursoAsignatura.objects.filter(filtro).order_by('-id')
                paging = MiPaginador(listado, 20)
                p = 1
                try:
                    paginasesion = 1
                    if 'paginador' in request.session:
                        paginasesion = int(request.session['paginador'])
                    if 'page' in request.GET:
                        p = int(request.GET['page'])
                    else:
                        p = paginasesion
                    try:
                        page = paging.page(p)
                    except:
                        p = 1
                    page = paging.page(p)
                except:
                    page = paging.page(p)
                request.session['paginador'] = p
                data['paging'] = paging
                data['rangospaging'] = paging.rangos_paginado(p)
                data['page'] = page
                data["url_vars"] = url_vars
                data['listado'] = page.object_list
                data['totcount'] = listado.count()
                request.session['viewactivo'] = 1
                return render(request, 'curso/view.html', data)
            
            elif action == 'addcurso':
                try:
                    data['title'] = u'Adicionar Curso'
                    form = CursoForm()
                    form.fields['profesor'].queryset = Persona.objects.filter(status=True, perfil=2)
                    form.fields['estudiantes'].queryset = Persona.objects.filter(status=True, perfil=1)
                    data['form'] = form
                    template = "curso/modal/formcurso.html"
                    # return JsonResponse({"result": True, 'data': template.render(data)})
                    return render(request, template, data )
                except Exception as ex:
                    pass
        else:
            template='home.html'
            return render(request, template, data)
                


        