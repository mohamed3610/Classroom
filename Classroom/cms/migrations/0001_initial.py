# Generated by Django 5.1.3 on 2025-01-21 13:49

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('Users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CourseMaterial',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('file', models.FileField(upload_to='course_materials/')),
                ('description', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Grades',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(max_length=100)),
                ('score', models.DecimalField(decimal_places=2, max_digits=5)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='student_grades', to='Users.student')),
            ],
        ),
    ]
