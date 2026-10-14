from django.contrib import admin
from django.db.models import Sum
from django.http import HttpResponseNotAllowed, JsonResponse
from django.urls import path

from .models import LancamentoPontos, Participante


class LancamentoPontosInline(admin.TabularInline):
    model = LancamentoPontos
    extra = 0
    can_delete = False
    fields = ['criado_em', 'pontos', 'descricao', 'administrador']
    readonly_fields = fields

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Participante)
class ParticipanteAdmin(admin.ModelAdmin):
    change_list_template = 'admin/placar/participante/change_list.html'
    list_display = ['nome', 'pontos']
    list_per_page = 50
    readonly_fields = ['pontos']
    search_fields = ['nome']
    inlines = [LancamentoPontosInline]

    def has_delete_permission(self, request, obj=None):
        return False

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'total-pontos/',
                self.admin_site.admin_view(self.total_pontos_json),
                name='placar_participante_total_pontos',
            )
        ]
        return custom_urls + urls

    def total_pontos_json(self, request):
        if request.method != 'GET':
            return HttpResponseNotAllowed(['GET'])

        total = Participante.objects.aggregate(total=Sum('pontos'))['total'] or 0
        return JsonResponse({'total_pontos': total})

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['total_pontos'] = (
            Participante.objects.aggregate(total=Sum('pontos'))['total'] or 0
        )
        return super().changelist_view(request, extra_context=extra_context)
