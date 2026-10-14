import hashlib
import secrets

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core import signing
from django.db import IntegrityError, transaction
from django.db.models import F, Sum
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET

from .forms import (
    CadastroParticipanteForm,
    FiltroLancamentosForm,
    LancamentoPontosForm,
)
from .models import LancamentoPontos, Participante, RegistroNavegador


COOKIE_NAVEGADOR = 'placar_navegador'
IDADE_COOKIE_NAVEGADOR = 60 * 60 * 24 * 365
SAL_COOKIE_NAVEGADOR = 'placar.registro_navegador'


def _ler_token_navegador(request):
    cookie = request.COOKIES.get(COOKIE_NAVEGADOR)
    if not cookie:
        return None

    try:
        return signing.loads(
            cookie,
            salt=SAL_COOKIE_NAVEGADOR,
            max_age=IDADE_COOKIE_NAVEGADOR,
        )
    except signing.BadSignature:
        return None


def _definir_cookie_navegador(response, token, *, secure):
    response.set_cookie(
        COOKIE_NAVEGADOR,
        signing.dumps(token, salt=SAL_COOKIE_NAVEGADOR),
        max_age=IDADE_COOKIE_NAVEGADOR,
        httponly=True,
        secure=secure,
        samesite='Lax',
    )


def inicio(request):
    token_navegador = _ler_token_navegador(request)
    if request.method == 'POST':
        form = CadastroParticipanteForm(request.POST)
        if form.is_valid():
            if token_navegador is None:
                form.add_error(
                    None,
                    'Não foi possível identificar este navegador. Atualize a página e tente novamente.',
                )
            else:
                token_hash = hashlib.sha256(token_navegador.encode()).hexdigest()
                if RegistroNavegador.objects.filter(token_hash=token_hash).exists():
                    form.add_error(
                        None,
                        'Este navegador já realizou um cadastro. Só é permitido um cadastro por navegador.',
                    )
                else:
                    try:
                        with transaction.atomic():
                            participante = form.save()
                            RegistroNavegador.objects.create(
                                participante=participante,
                                token_hash=token_hash,
                            )
                    except IntegrityError:
                        if RegistroNavegador.objects.filter(token_hash=token_hash).exists():
                            form.add_error(
                                None,
                                'Este navegador já realizou um cadastro. Só é permitido um cadastro por navegador.',
                            )
                        elif Participante.objects.filter(
                            nome=form.cleaned_data['nome']
                        ).exists():
                            form.add_error(
                                'nome',
                                'Já existe um participante com este nome.',
                            )
                        else:
                            raise
                    else:
                        messages.success(request, 'Cadastro realizado com sucesso!')
                        return redirect('placar:inicio')
    else:
        form = CadastroParticipanteForm()

    participante_do_navegador = None
    if token_navegador is not None:
        token_hash = hashlib.sha256(token_navegador.encode()).hexdigest()
        registro = (
            RegistroNavegador.objects.select_related('participante')
            .filter(token_hash=token_hash)
            .first()
        )
        if registro is not None:
            participante_do_navegador = registro.participante

    response = render(
        request,
        'placar/inicio.html',
        {
            'form': form,
            'participantes': Participante.objects.all(),
            'participante_do_navegador': participante_do_navegador,
        },
    )
    if token_navegador is None and request.method == 'GET':
        _definir_cookie_navegador(
            response,
            secrets.token_urlsafe(32),
            secure=request.is_secure(),
        )
    return response


@staff_member_required
def gerenciar_pontos(request):
    if request.method == 'POST':
        form = LancamentoPontosForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                participante = Participante.objects.select_for_update().get(
                    pk=form.cleaned_data['participante'].pk
                )
                pontos_adicionados = form.cleaned_data['pontos']
                Participante.objects.filter(pk=participante.pk).update(
                    pontos=F('pontos') + pontos_adicionados
                )
                lancamento = form.save(commit=False)
                lancamento.participante = participante
                lancamento.administrador = request.user
                lancamento.save()

            messages.success(
                request,
                f'{pontos_adicionados} ponto(s) adicionado(s) para {participante.nome}.',
            )
            return redirect('placar:gerenciar_pontos')
    else:
        form = LancamentoPontosForm()

    filtro_form = FiltroLancamentosForm(request.GET or None)
    lancamentos = LancamentoPontos.objects.select_related(
        'participante',
        'administrador',
    )
    if filtro_form.is_valid() and filtro_form.cleaned_data['participante']:
        lancamentos = lancamentos.filter(
            participante=filtro_form.cleaned_data['participante']
        )

    contexto = {
        'form': form,
        'filtro_form': filtro_form,
        'lancamentos': lancamentos[:30],
        'total_pontos': Participante.objects.aggregate(total=Sum('pontos'))['total']
        or 0,
    }
    return render(request, 'placar/gerenciar_pontos.html', contexto)


@staff_member_required
@require_GET
def total_pontos_json(request):
    total = Participante.objects.aggregate(total=Sum('pontos'))['total'] or 0
    return JsonResponse({'total_pontos': total})


@require_GET
def ranking_json(request):
    participantes = Participante.objects.all()
    return JsonResponse(
        {
            'participantes': [
                {
                    'posicao': posicao,
                    'nome': participante.nome,
                    'pontos': participante.pontos,
                }
                for posicao, participante in enumerate(participantes, start=1)
            ]
        }
    )
