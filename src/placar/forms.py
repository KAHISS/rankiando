from django import forms

from .models import LancamentoPontos, Participante


class CadastroParticipanteForm(forms.ModelForm):
    class Meta:
        model = Participante
        fields = ['nome']
        widgets = {
            'nome': forms.TextInput(
                attrs={
                    'autocomplete': 'name',
                    'placeholder': 'Digite seu nome',
                    'maxlength': 80,
                }
            )
        }

    def clean_nome(self):
        return ' '.join(self.cleaned_data['nome'].split())


class LancamentoPontosForm(forms.ModelForm):
    class Meta:
        model = LancamentoPontos
        fields = ['participante', 'pontos', 'descricao']
        widgets = {
            'pontos': forms.NumberInput(attrs={'min': 1, 'step': 1}),
            'descricao': forms.TextInput(
                attrs={
                    'placeholder': 'Motivo do lançamento (opcional)',
                    'maxlength': 200,
                }
            ),
        }


class FiltroLancamentosForm(forms.Form):
    participante = forms.ModelChoiceField(
        queryset=Participante.objects.none(),
        required=False,
        empty_label='Todos os participantes',
        label='Filtrar por participante',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['participante'].queryset = Participante.objects.order_by('nome')
