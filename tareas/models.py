from django.db import models
from django.contrib.auth.models import User
from utils.models import ModeloBase
from django.core import validators
from Tarea.validators import vcedula, SoloNumeros, SoloLetras
from Tarea.funciones import Ruta
# Create your models here.
SEXO=(
   (0,'---------'),
   (1,'Masculino'),
   (2,'Femenino'),
    )
PERFIL_USUARIO=(
   (0,'----------'),
   (1,'Estudiante'),
   (2,'Docente'),
   (3,'Administrativo'),
    )
TIPO_RECURSO=(
   (0,'----------'),
   (1,'Video'),
   (2,'Archivo'),
   (3,'Enlace'),
    )
class Persona(ModeloBase):
    user=models.OneToOneField(User, on_delete=models.CASCADE,)
    nombres=models.CharField(max_length=100, validators=[validators.MinLengthValidator(4)], verbose_name=u'Nombres')
    apellido1=models.CharField(max_length=100, validators=[validators.MinLengthValidator(4)],verbose_name=u'Primer apellido' )
    apellido2=models.CharField(max_length=100, validators=[validators.MinLengthValidator(4)], verbose_name=u'Segundo apellido')
    cedula=models.CharField(max_length=10, validators=[validators.MinLengthValidator(10), vcedula],)
    genero=models.IntegerField(choices=SEXO, default=0, verbose_name=u'Genero')
    perfil=models.IntegerField(choices=PERFIL_USUARIO, default=0, verbose_name=u'Tipo de usuario')
    fecha_nacimiento=models.DateField(verbose_name=u'Fecha de nacimiento')
    telefono=models.CharField(max_length=20, validators=[validators.MinLengthValidator(10), SoloNumeros], verbose_name=u'Número de telefono')
    direccion=models.CharField(max_length=100, verbose_name=u'Dirección de domicilio')
    ciudad=models.CharField(max_length=100,verbose_name=u'Ciudad')
    
    picture=models.ImageField(
        upload_to='Fotos',verbose_name=u'Foto',
        blank=True,
        null=True,)

    def __str__(self):
        #return username
        return (f'{self.nombres} {self.apellido1} {self.apellido2}')
    def nombre_simple(self):
        nombres=self.nombres.split(' ')
        return (f'{nombres[0]} {self.apellido1}')
class Curso(ModeloBase):
    nombre = models.CharField(default='',verbose_name=u'Nombre de la curso', max_length=250)
    paralelo = models.CharField(default='',verbose_name=u'Paralelo', max_length=250)
    descripcion = models.TextField(verbose_name=u'descripcion')
    cupo = models.IntegerField(default=0, verbose_name=u'Cupo')
    cerrado = models.BooleanField(default=False, verbose_name=u"Cerrado")

    def __str__(self):
        return u'%s' % self.nombre

    class Meta:
        verbose_name = u"Curso"
        verbose_name_plural = u"Cursos"
        ordering = ['nombre']
        unique_together = ('nombre',)

class Asignatura(ModeloBase):
    nombre = models.CharField(default='', max_length=250, verbose_name=u'Nombre')
    codigo = models.CharField(default='', max_length=30, verbose_name=u'Codigo')
    modulo = models.BooleanField(default=False, verbose_name=u'Modulos')

    def __str__(self):
        return u'%s %s' % (self.nombre, "[" + self.codigo + "]" if self.codigo else "")

    class Meta:
        verbose_name = u"Asignatura"
        verbose_name_plural = u"Asignaturas"
        ordering = ["nombre"]
        unique_together = ('nombre',)

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.upper().strip()
        self.codigo = self.codigo.upper().strip()
        super(Asignatura, self).save(*args, **kwargs)

class CursoAsignatura(ModeloBase):
    curso = models.ForeignKey(Curso, verbose_name=u'Curso', on_delete=models.CASCADE)
    asignatura = models.ForeignKey(Asignatura, verbose_name=u'Asignatura', on_delete=models.CASCADE)
    profesor = models.ForeignKey(Persona, blank=True, null=True, verbose_name=u'Profesor', on_delete=models.CASCADE)
    cerrada = models.BooleanField(default=False, verbose_name=u'Cerrado')
    estudiantes = models.ManyToManyField(Persona, verbose_name=u'Estudiantes inscritos en la asignatura', related_name='+')

    def __str__(self):
        return u'%s - %s' % (self.curso, self.asignatura)

    class Meta:
        unique_together = ('curso', 'asignatura',)
    
class Recurso(ModeloBase):
    titulo = models.CharField(max_length=200)
    descripcion = models.CharField(default='', max_length=5000, verbose_name=u'Descripción')
    archivo = models.FileField(upload_to='Recursos', blank=True, null=True, verbose_name=u'Archivo')
    enlace= models.CharField(default='', max_length=5000, verbose_name=u'Enlace')

    def __str__(self):
        return self.titulo

class Task(ModeloBase):
  asignatura = models.ForeignKey(CursoAsignatura, on_delete=models.CASCADE, blank=True, null=True, verbose_name=u'Asignatura a la que pertenece la tarea')
  recursos = models.ManyToManyField(Recurso, verbose_name=u'Recursos de tarea')
  title = models.CharField(default='', max_length=100, verbose_name=u'Titulo')
  description = models.CharField(default='', max_length=5000, verbose_name=u'Descripción')
  important = models.BooleanField(default=False)
  profesor = models.ForeignKey(Persona, blank=True, null=True, on_delete=models.CASCADE)

  def __str__(self):
    return self.titulo + ' - ' + self.profesor










