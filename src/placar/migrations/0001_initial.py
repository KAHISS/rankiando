import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Participante',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                ('nome', models.CharField(max_length=80, unique=True, verbose_name='nome')),
                (
                    'pontos',
                    models.PositiveIntegerField(
                        default=0,
                        validators=[django.core.validators.MinValueValidator(0)],
                        verbose_name='pontos',
                    ),
                ),
            ],
            options={
                'verbose_name': 'participante',
                'verbose_name_plural': 'participantes',
                'ordering': ['-pontos', 'nome'],
            },
        ),
    ]
