# Generated by Django 4.1.5 on 2023-03-04 21:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tareas', '0007_remove_persona_facebook_remove_persona_github_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='persona',
            name='picture',
            field=models.ImageField(blank=True, null=True, upload_to='Fotos', verbose_name='Foto'),
        ),
    ]
