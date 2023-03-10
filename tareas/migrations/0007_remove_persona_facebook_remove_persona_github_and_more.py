# Generated by Django 4.1.5 on 2023-03-04 18:07

import Tarea.funciones
import Tarea.validators
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tareas', '0006_remove_asignatura_creditos'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='persona',
            name='facebook',
        ),
        migrations.RemoveField(
            model_name='persona',
            name='github',
        ),
        migrations.RemoveField(
            model_name='persona',
            name='linkedin',
        ),
        migrations.RemoveField(
            model_name='persona',
            name='twitter',
        ),
        migrations.AlterField(
            model_name='persona',
            name='apellido1',
            field=models.CharField(max_length=100, validators=[django.core.validators.MinLengthValidator(4)], verbose_name='Primer apellido'),
        ),
        migrations.AlterField(
            model_name='persona',
            name='apellido2',
            field=models.CharField(max_length=100, validators=[django.core.validators.MinLengthValidator(4)], verbose_name='Segundo apellido'),
        ),
        migrations.AlterField(
            model_name='persona',
            name='cedula',
            field=models.CharField(max_length=10, validators=[django.core.validators.MinLengthValidator(10), Tarea.validators.vcedula]),
        ),
        migrations.AlterField(
            model_name='persona',
            name='ciudad',
            field=models.CharField(max_length=100, verbose_name='Ciudad'),
        ),
        migrations.AlterField(
            model_name='persona',
            name='direccion',
            field=models.CharField(max_length=100, verbose_name='Dirección de domicilio'),
        ),
        migrations.AlterField(
            model_name='persona',
            name='fecha_nacimiento',
            field=models.DateField(default=None, verbose_name='Fecha de nacimiento'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='persona',
            name='genero',
            field=models.IntegerField(choices=[(0, '---------'), (1, 'Masculino'), (2, 'Femenino')], default=0, verbose_name='Genero'),
        ),
        migrations.AlterField(
            model_name='persona',
            name='nombres',
            field=models.CharField(max_length=100, validators=[django.core.validators.MinLengthValidator(4)], verbose_name='Nombres'),
        ),
        migrations.AlterField(
            model_name='persona',
            name='perfil',
            field=models.IntegerField(choices=[(0, '----------'), (1, 'Estudiante'), (2, 'Docente'), (3, 'Administrativo')], default=0, verbose_name='Tipo de usuario'),
        ),
        migrations.AlterField(
            model_name='persona',
            name='picture',
            field=models.ImageField(blank=True, null=True, upload_to=Tarea.funciones.Ruta, verbose_name='Foto'),
        ),
        migrations.AlterField(
            model_name='persona',
            name='telefono',
            field=models.CharField(max_length=20, validators=[django.core.validators.MinLengthValidator(10), Tarea.validators.SoloNumeros], verbose_name='Número de telefono'),
        ),
    ]
