from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class Participante(models.Model):
    nome = models.CharField('nome', max_length=80, unique=True)
    pontos = models.PositiveIntegerField(
        'pontos',
        default=0,
        validators=[MinValueValidator(0)],
    )

    class Meta:
        ordering = ['-pontos', 'nome']
        verbose_name = 'participante'
        verbose_name_plural = 'participantes'

    def __str__(self):
        return self.nome


class RegistroNavegador(models.Model):
    participante = models.OneToOneField(
        Participante,
        on_delete=models.CASCADE,
        related_name='registro_navegador',
    )
    token_hash = models.CharField(max_length=64, unique=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'registro de navegador'
        verbose_name_plural = 'registros de navegadores'

    def __str__(self):
        return f'Registro de {self.participante}'


class LancamentoPontos(models.Model):
    participante = models.ForeignKey(
        Participante,
        on_delete=models.CASCADE,
        related_name='lancamentos',
        verbose_name='participante',
    )
    pontos = models.PositiveIntegerField(
        'pontos adicionados',
        validators=[MinValueValidator(1)],
    )
    descricao = models.CharField('motivo', max_length=200, blank=True)
    administrador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='lancamentos_registrados',
    )
    criado_em = models.DateTimeField('data do lançamento', auto_now_add=True)

    class Meta:
        ordering = ['-criado_em', '-pk']
        verbose_name = 'lançamento de pontos'
        verbose_name_plural = 'lançamentos de pontos'

    def __str__(self):
        return f'+{self.pontos} pontos para {self.participante}'
