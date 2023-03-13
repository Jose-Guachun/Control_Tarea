import os.path
from urllib.parse import urlencode

from django.forms import model_to_dict
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.urls import reverse, reverse_lazy
from tareas.forms import *
# Django decorators
from django.views.generic.edit import FormView
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.db import transaction
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.db.models import Q
from django.contrib import messages

from .models import *
from .forms import TaskForm
from Tarea.funciones import MiPaginador, generar_nombre
from Tarea.settings import DEBUG, BASE_DIR
import pyqrcode
from datetime import datetime


def signup(request):
    if request.method == 'GET':
        return render(request, 'signup.html', {"form": UserCreationForm})
    else:
        try:
            form = UserCreationForm(request.POST)
            if form.is_valid():
                user = User.objects.create_user(request.POST["username"], password=request.POST["password1"])
                user.save()
                login(request, user)
                return redirect('login')
            else:
                return render(request, 'signup.html', {"form": form})
        except Exception as ex:
            return render(request, 'signup.html', {"form": UserCreationForm(request.POST), "error": str(ex)})


@login_required
def signout(request):
    logout(request)
    return redirect('login')


class LoginView(FormView):
    # login view
    template_name = 'signin.html'
    form_class = LoginForm
    success_url = reverse_lazy('home')

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
def home(request):
    data={}
    usuario = request.user
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
                            newfile._name = generar_nombre(f'{request.user.username}', newfile._name)
                            instance.picture = newfile
                        instance.save(request)
                    return redirect('home')
                else:
                    return render(request, 'actualizarperfil.html', {"form": form})
            except Exception as ex:
                transaction.set_rollback(True)
                return render(request, 'actualizarperfil.html',
                              {"error": "Error: {}".format(str(ex)), "form": PersonaForm(request.POST)})
    else:
        if not Persona.objects.filter(user=usuario).exists():
            data['form']=PersonaForm()
            template = 'actualizarperfil.html'
        else:
            data['persona'] = Persona.objects.get(user=usuario)
            template = 'home.html'
        return render(request, template, data)

@login_required
@transaction.atomic()
def cargarsistema(request, action):
    data = {}
    usuario = request.user
    persona = Persona.objects.filter(user=usuario)
    if DEBUG:
        DOMINIO_SISTEMA = 'http://localhost:8000/'
    else:
        DOMINIO_SISTEMA = None
    estudiantes_id=[]
    cursos=CursoAsignatura.objects.filter(status=True, cerrada=False)
    for curso in cursos:
        for estudiante in curso.estudiantes.all():
            estudiantes_id.append(estudiante.id)
    if request.method == 'POST':
        action = request.POST.get('action',action)
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
                            newfile._name = generar_nombre(f'{request.user.username}', newfile._name)
                            instance.picture = newfile
                        instance.save(request)
                    else:
                        instance = Persona.objects.get(user=request.user)
                        instance.nombres=form.cleaned_data['nombres']
                        instance.apellido1=form.cleaned_data['apellido1']
                        instance.apellido2=form.cleaned_data['apellido2']
                        instance.cedula=form.cleaned_data['cedula']
                        instance.genero=form.cleaned_data['genero']
                        instance.perfil=form.cleaned_data['perfil']
                        instance.fecha_nacimiento=form.cleaned_data['fecha_nacimiento']
                        instance.telefono=form.cleaned_data['telefono']
                        instance.direccion=form.cleaned_data['direccion']
                        instance.ciudad=form.cleaned_data['ciudad']
                        instance.save(request)
                        if 'picture' in request.FILES:
                            newfile = request.FILES['picture']
                            newfile._name = generar_nombre(f'{request.user.username}', newfile._name)
                            instance.picture = newfile
                        instance.save(request)
                    return redirect('home')
                else:
                    return render(request, 'actualizarperfil.html', {"form": form})
            except Exception as ex:
                transaction.set_rollback(True)
                return render(request, 'actualizarperfil.html',
                              {"error": "Error: {}".format(str(ex)), "form": PersonaForm(request.POST)})

        if action == 'addcurso':
            try:
                form = CursoAsignaturaForm(request.POST)
                form.fields['profesor'].queryset = Persona.objects.filter(status=True, perfil=2)
                form.fields['estudiantes'].queryset = Persona.objects.filter(status=True, perfil=1)
                if form.is_valid():
                    instance = CursoAsignatura(curso=form.cleaned_data['curso'],
                                               asignatura=form.cleaned_data['asignatura'],
                                               profesor=form.cleaned_data['profesor'],
                                               )
                    instance.save(request)
                    for estuidante in form.cleaned_data['estudiantes']:
                        instance.estudiantes.add(estuidante)
                    return redirect(reverse_lazy('sistema', kwargs={'action':'cursos'}))
                else:
                    return render(request, 'curso/modal/formcurso.html',
                                  {"form": form,  "errors": [{v[0]} for k, v in form.errors.items()]})
                    # return redirect(reverse_lazy('sistema', kwargs={'action': 'addcurso'}))
                    # return render(request, 'curso/modal/formcurso.html',{"form": CursoForm(request.POST),  "errors": [{k: v[0]} for k, v in form.errors.items()]})
            except Exception as ex:
                form = CursoAsignaturaForm(request.POST)
                form.fields['profesor'].queryset = Persona.objects.filter(status=True, perfil=2)
                form.fields['estudiantes'].queryset = Persona.objects.filter(status=True, perfil=1)
                transaction.set_rollback(True)
                messages.error(request, str(ex))
                return render(request, 'curso/modal/formcurso.html',
                              {"form": form})

        if action == 'editcurso':
            try:
                id=request.POST['id']
                curso_a=CursoAsignatura.objects.get(id=id)
                form = CursoAsignaturaForm(request.POST, instance=curso_a)
                form.fields['profesor'].queryset = Persona.objects.filter(status=True, perfil=2)
                form.fields['estudiantes'].queryset = Persona.objects.filter(status=True, perfil=1)
                if form.is_valid():
                    curso_a.curso=form.cleaned_data['curso']
                    curso_a.asignatura=form.cleaned_data['asignatura']
                    curso_a.profesor=form.cleaned_data['profesor']
                    curso_a.save(request)
                    curso_a.estudiantes.clear()
                    for estuidante in form.cleaned_data['estudiantes']:
                        curso_a.estudiantes.add(estuidante)
                    return redirect(reverse_lazy('sistema', kwargs={'action': 'cursos'}))
                else:
                    return render(request, 'curso/modal/formcurso.html',
                                  {"form": form,'id':request.POST['id'],'curso_a':curso_a, "errors": [{v[0]} for k, v in form.errors.items()]})

                    # return render(request, 'curso/modal/formcurso.html',{"form": CursoAsignaturaForm(request.POST),  "errors": [{k: v[0]} for k, v in form.errors.items()]})
            except Exception as ex:
                data['form'] = form = CursoAsignaturaForm(request.POST)
                data['id'] = request.POST['id']
                data['curso_a'] = curso_a = CursoAsignatura.objects.get(id=request.POST['id'])
                form.fields['profesor'].queryset = Persona.objects.filter(status=True, perfil=2)
                form.fields['estudiantes'].queryset = Persona.objects.filter(status=True, perfil=1)
                transaction.set_rollback(True)
                messages.error(request, str(ex))
                return render(request, 'curso/modal/formcurso.html',data)

        if action == 'delcurso':
            try:
                instancia = CursoAsignatura.objects.get(pk=request.POST['id'])
                instancia.delete()
                res_json = {"error": False}
            except Exception as ex:
                res_json = {'error': True, "message": "Error: {}".format(ex)}
            return JsonResponse(res_json, safe=False)

        if action == 'addtarea':
            try:
                form = TaskForm(request.POST)
                idp=request.POST['idp']
                if form.is_valid():
                    archivo = None
                    if request.FILES:
                        archivo = request.FILES['archivo']
                    instance = Task(asignatura_id=idp,
                                   title=form.cleaned_data['title'],
                                   description=form.cleaned_data['description'],
                                   archivo=archivo,
                                    )
                    instance.save(request)
                    for recurso in form.cleaned_data['recursos']:
                        instance.recursos.add(recurso)
                    # Generar codigo QR
                    nombre_qr = 'qr' + str(instance.id) + '.png'
                    carpeta_qr = 'ImageQR'
                    directorio = os.path.join(os.path.join(BASE_DIR, 'media', carpeta_qr))
                    ruta_qr = directorio + '\\' + nombre_qr
                    try:
                        os.stat(directorio)
                    except:
                        os.mkdir(directorio)
                    if os.path.isfile(ruta_qr):
                        os.remove(ruta_qr)
                    version = datetime.now().strftime('%Y%m%d_%H%M%S%f')
                    qr_url = pyqrcode.create(f'{DOMINIO_SISTEMA}media/{carpeta_qr}/{nombre_qr}?v={version}')
                    qr_png = qr_url.png(ruta_qr, 16, '#000000')
                    instance.archivo_qr = f'{carpeta_qr}/{nombre_qr}'
                    instance.save(request)
                    # Generar codigo QR
                    # Se construye la URL de la nueva vista con los parámetros
                    url = reverse('sistema', kwargs={'action': 'tareas'}) + '?' + urlencode({'id': idp})
                    # Se redirige al usuario a la nueva URL
                    return redirect(url)
                else:
                    return render(request, 'curso/modal/formtarea.html',
                                  {"form": TaskForm(request.POST),
                                   'idp': idp})
                    # return render(request, 'curso/modal/formcurso.html',{"form": CursoForm(request.POST),  "errors": [{k: v[0]} for k, v in form.errors.items()]})
            except Exception as ex:
                #transaction.rollback()
                messages.error(request, str(ex))
                return render(request, 'curso/modal/formtarea.html',
                              {"error": "Error: {}".format(str(ex)), "form": TaskForm(request.POST),'idp':request.POST['id']})
                # return redirect(reverse_lazy('sistema', kwargs={'action': f'addtarea?idp={request.POST["id"]}'}))

        if action == 'edittarea':
            try:
                id = request.POST['id']
                idp = request.POST['idp']
                tarea = Task.objects.get(id=id)
                form = TaskForm(request.POST, instance=tarea)
                if form.is_valid():
                    if request.FILES:
                        tarea .archivo = request.FILES['archivo']
                    tarea.title = form.cleaned_data['title']
                    tarea.description = form.cleaned_data['description']
                    tarea.save(request)
                    tarea.recursos.clear()
                    for recurso in form.cleaned_data['recursos']:
                        tarea.recursos.add(recurso)
                    url = reverse('sistema', kwargs={'action': 'tareas'}) + '?' + urlencode({'id': tarea.asignatura.id})
                    # Se redirige al usuario a la nueva URL
                    return redirect(url)
                else:
                    return render(request, 'curso/modal/formtarea.html',
                                  {"form": TaskForm(request.POST),
                                   'title': 'Editar Tare',
                                   'id': id,
                                   'idp': tarea.asignatura.id})
                # return render(request, 'curso/modal/formcurso.html',{"form": CursoAsignaturaForm(request.POST),  "errors": [{k: v[0]} for k, v in form.errors.items()]})
            except Exception as ex:
                # transaction.set_rollback(True)
                messages.error(request, str(ex))
                return render(request, 'curso/modal/formtarea.html',
                              {"error": "Error: {}".format(str(ex)), "form": TaskForm(request.POST),
                               'title': 'Editar Tarea',
                               'id': request.POST['id'],
                               'idp': request.POST['idp']})

        if action == 'deltarea':
            try:
                instancia = Task.objects.get(pk=request.POST['id'])
                instancia.delete()
                res_json = {"error": False}
            except Exception as ex:
                res_json = {'error': True, "message": "Error: {}".format(ex)}
            return JsonResponse(res_json, safe=False)

        # Recursos
        if action == 'addrecurso':
            try:
                form = RecursoForm(request.POST, request.FILES)
                if form.is_valid():
                    enlace = form.cleaned_data['enlace']
                    archivo = None
                    if request.FILES:
                        archivo = request.FILES['archivo']
                    if Recurso.objects.filter(status=True, enlace=enlace).exists():
                        messages.error(request, f'Enlace de recurso ya existe.')
                        return redirect(reverse_lazy('sistema', kwargs={'action': 'addrecurso'}))
                    if Recurso.objects.filter(status=True, archivo=archivo).exists():
                        messages.error(request, f'Archivo de recurso ya existe.')
                        return redirect(reverse_lazy('sistema', kwargs={'action': 'addrecurso'}))
                    if not enlace and not archivo:
                        messages.error(request, f'Debe ingresar enlace o el archivo del recurso.')
                        return redirect(reverse_lazy('sistema', kwargs={'action': 'addrecurso'}))
                    instance = Recurso(titulo=form.cleaned_data['titulo'],
                                               descripcion=form.cleaned_data['descripcion'],
                                               enlace=enlace,
                                               archivo = archivo
                    )
                    instance.save(request)
                    # for estuidante in form.cleaned_data['estudiantes']:
                    #     instance.estudiantes.add(estuidante)
                    return redirect(reverse_lazy('sistema', kwargs={'action':'recursos'}))
                else:
                    messages.error(request, [v[0]for k, v in form.errors.items()])
                    return redirect(reverse_lazy('sistema', kwargs={'action': 'addrecurso'}))
                    # return render(request, 'curso/modal/formcurso.html',{"form": CursoForm(request.POST),  "errors": [{k: v[0]} for k, v in form.errors.items()]})
            except Exception as ex:
                transaction.set_rollback(True)
                messages.error(request, '')
                return redirect(reverse_lazy('sistema', kwargs={'action': 'addrecurso'}))

        if action == 'editrecurso':
            try:
                id=request.POST['id']
                recurso=Recurso.objects.get(id=id)
                form = RecursoForm(request.POST, instance=recurso)
                if form.is_valid():
                    if Recurso.objects.filter(status=True, enlace=form.cleaned_data['enlace']).exclude(id=id).exists():
                        messages.error(request, f'Enlace de recurso ya existe.')
                        return redirect(reverse_lazy('sistema', kwargs={'action': 'addrecurso'}))
                    if Recurso.objects.filter(status=True, archivo=form.cleaned_data['archivo']).exclude(id=id).exists():
                        messages.error(request, f'Archivo de recurso ya existe.')
                    recurso.titulo=form.cleaned_data['titulo']
                    recurso.descripcion=form.cleaned_data['descripcion']
                    recurso.enlace=form.cleaned_data['enlace']
                    recurso.archivo=form.cleaned_data['archivo']
                    recurso.save(request)
                    # recurso.estudiantes.clear()
                    # for estuidante in form.cleaned_data['estudiantes']:
                    #     recurso.estudiantes.add(estuidante)
                else:
                    messages.error(request, [v[0] for k, v in form.errors.items()])
                return redirect(reverse_lazy('sistema', kwargs={'action': 'recursos'}))
                    # return render(request, 'curso/modal/formcurso.html',{"form": CursoAsignaturaForm(request.POST),  "errors": [{k: v[0]} for k, v in form.errors.items()]})
            except Exception as ex:
                transaction.set_rollback(True)
                messages.error(request, 'Error. Por favor intentelo mas tarde')
                return redirect(reverse_lazy('sistema', kwargs={'action': 'recursos'}))

        if action == 'delrecurso':
            try:
                instancia = Recurso.objects.get(pk=request.POST['id'])
                # Valida que el registro no esté en uso

                instancia.status = False
                instancia.save(request)
                res_json = {"error": False}
            except Exception as ex:
                res_json = {'error': True, "message": "Error: {}".format(ex)}
            return JsonResponse(res_json, safe=False)

        return JsonResponse({"result": "bad", "mensaje": u"Solicitud Incorrecta."})
    else:
        if not persona:
            template = 'actualizarperfil.html'
            return render(request, template, {"form": PersonaForm()})
            # if 'action' in request.GET:
            # data['action'] = action = request.GET['action']
        data['persona'] = persona = Persona.objects.get(user=usuario)
        data['action'] = action

        if action=='addpersona':
            if not Persona.objects.filter(user=usuario).exists():
                data['form'] = PersonaForm()
                template = 'actualizarperfil.html'
            else:
                data['persona'] = persona=Persona.objects.get(user=usuario)
                data['form'] = PersonaForm(initial=model_to_dict(persona))
                template = 'actualizarperfil.html'
            return render(request, template, data)

        elif action == 'cursos':
            data['title'] = 'Cursos'
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
                form = CursoAsignaturaForm()
                form.fields['profesor'].queryset = Persona.objects.filter(status=True, perfil=2)
                form.fields['estudiantes'].queryset = Persona.objects.filter(status=True, perfil=1).exclude(id__in=estudiantes_id)
                data['form'] = form
                template = "curso/modal/formcurso.html"
                return render(request, template, data)
            except Exception as ex:
                pass

        elif action == 'editcurso':
            try:
                data['title'] = u'Adicionar Curso'
                id=request.GET["id"]
                data['curso_a']= curso_a =CursoAsignatura.objects.get(id=id)
                form = CursoAsignaturaForm(initial=model_to_dict(curso_a))
                form.fields['profesor'].queryset = Persona.objects.filter(status=True, perfil=2)
                form.fields['estudiantes'].queryset = Persona.objects.filter(status=True, perfil=1)
                data['form'] = form
                template = "curso/modal/formcurso.html"
                return render(request, template, data)
            except Exception as ex:
                pass

        elif action == 'tareas':
            data['title'] = 'Tareas'
            data['curso_a']=curso_a=CursoAsignatura.objects.get(id=request.GET['id'])
            search, filtro, url_vars = request.GET.get('s', ''), Q(status=True), f'&id={curso_a.id}'
            if search:
                filtro = filtro & Q(nombre__icontains=search)
                url_vars += '&s=' + search
                data['search'] = search
            listado =Task.objects.filter(filtro).order_by('-id')
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
            return render(request, 'curso/viewtareas.html', data)

        elif action == 'addtarea':
            try:
                data['idp']=request.GET['idp']
                data['title'] = u'Adicionar Tarea'
                form = TaskForm()
                data['form'] = form
                template = "curso/modal/formtarea.html"
                return render(request, template, data)
            except Exception as ex:
                pass

        elif action == 'edittarea':
            try:
                data['title'] = u'Editar Tarea'
                data['idp']= idp = request.GET["idp"]
                data['id']= id = request.GET["id"]
                data['tarea'] = tarea = Task.objects.get(id=id)
                form = TaskForm(initial=model_to_dict(tarea))
                data['form'] = form
                template = "curso/modal/formtarea.html"
                return render(request, template, data)
            except Exception as ex:
                pass
        # Recursos
        if action == 'recursos':
            data['title'] = 'Recursos'
            search, filtro, url_vars = request.GET.get('s', ''), Q(status=True), ''
            if search:
                filtro = filtro & Q(titulo__icontains=search)
                url_vars += '&s=' + search
                data['search'] = search
            listado = Recurso.objects.filter(filtro).order_by('-id')
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
            return render(request, 'recurso/view.html', data)

        elif action == 'addrecurso':
            try:
                data['title'] = u'Adicionar Recurso'
                form = RecursoForm()
                # form.fields['profesor'].queryset = Persona.objects.filter(status=True, perfil=2)
                # form.fields['estudiantes'].queryset = Persona.objects.filter(status=True, perfil=1)
                data['form'] = form
                template = "recurso/modal/formrecurso.html"
                return render(request, template, data)
            except Exception as ex:
                pass

        elif action == 'editrecurso':
            try:
                data['title'] = u'Adicionar Recurso'
                id=request.GET["id"]
                data['recurso']= recurso =Recurso.objects.get(id=id)
                form = RecursoForm(initial=model_to_dict(recurso))
                # form.fields['profesor'].queryset = Persona.objects.filter(status=True, perfil=2)
                # form.fields['estudiantes'].queryset = Persona.objects.filter(status=True, perfil=1)
                data['form'] = form
                template = "recurso/modal/formrecurso.html"
                return render(request, template, data)
            except Exception as ex:
                pass

        elif action == 'tareasestudiante':
            try:
                data['title'] = 'Tareas Asignadas'
                search, filtro, url_vars = request.GET.get('s', ''), Q(status=True, asignatura__estudiantes=persona), f''
                if search:
                    filtro = filtro & Q(nombre__icontains=search)
                    url_vars += '&s=' + search
                    data['search'] = search
                data['cursos']=CursoAsignatura.objects.filter(status=True, estudiantes=persona).order_by('-id')
                listado =Task.objects.filter(filtro).order_by('-id')
                paging = MiPaginador(listado, 10)
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
                return render(request, 'curso/viewtareasestudiante.html', data)
            except Exception as ex:
                pass
        else:
            template = 'home.html'
            return render(request, template, data)

def generar_qr(request, tarea):
    pass