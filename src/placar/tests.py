from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from .models import LancamentoPontos, Participante


class RankingTests(TestCase):
    def test_server_bind_address_is_allowed(self):
        response = self.client.get('/', HTTP_HOST='0.0.0.0:8000')

        self.assertEqual(response.status_code, 200)

    def test_participant_can_register_with_a_normalized_name(self):
        self.client.get(reverse('placar:inicio'))
        response = self.client.post(reverse('placar:inicio'), {'nome': '  Ana   Silva  '})

        self.assertRedirects(response, reverse('placar:inicio'))
        self.assertTrue(Participante.objects.filter(nome='Ana Silva').exists())

    def test_duplicate_name_is_rejected(self):
        Participante.objects.create(nome='Ana Silva')
        self.client.get(reverse('placar:inicio'))

        response = self.client.post(reverse('placar:inicio'), {'nome': 'Ana Silva'})

        self.assertEqual(response.status_code, 200)
        self.assertIn('nome', response.context['form'].errors)
        self.assertEqual(Participante.objects.count(), 1)

    def test_browser_can_register_only_once(self):
        self.client.get(reverse('placar:inicio'))
        registration_url = reverse('placar:inicio')

        first_response = self.client.post(registration_url, {'nome': 'Ana'})
        second_response = self.client.post(registration_url, {'nome': 'Bruna'})

        self.assertRedirects(first_response, registration_url)
        self.assertContains(second_response, 'já realizou um cadastro')
        self.assertEqual(Participante.objects.count(), 1)

    def test_registration_requires_a_browser_cookie(self):
        response = self.client.post(reverse('placar:inicio'), {'nome': 'Ana'})

        self.assertContains(response, 'Atualize a página e tente novamente.')
        self.assertFalse(Participante.objects.exists())

    def test_different_browsers_can_register_separately(self):
        registration_url = reverse('placar:inicio')
        first_browser = Client()
        second_browser = Client()
        first_browser.get(registration_url)
        second_browser.get(registration_url)

        first_browser.post(registration_url, {'nome': 'Ana'})
        second_browser.post(registration_url, {'nome': 'Bruna'})

        self.assertEqual(Participante.objects.count(), 2)

    def test_ranking_is_ordered_by_points_then_name(self):
        Participante.objects.create(nome='Bruna', pontos=10)
        Participante.objects.create(nome='Carla', pontos=10)
        Participante.objects.create(nome='Ana', pontos=15)

        response = self.client.get(reverse('placar:ranking_json'))

        self.assertEqual(
            response.json()['participantes'],
            [
                {'posicao': 1, 'nome': 'Ana', 'pontos': 15},
                {'posicao': 2, 'nome': 'Bruna', 'pontos': 10},
                {'posicao': 3, 'nome': 'Carla', 'pontos': 10},
            ],
        )

    def test_admin_total_updates_from_saved_points(self):
        participant = Participante.objects.create(nome='Ana', pontos=3)
        staff_user = get_user_model().objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='test-password',
        )
        self.client.force_login(staff_user)
        total_url = reverse('admin:placar_participante_total_pontos')

        self.assertEqual(self.client.get(total_url).json(), {'total_pontos': 3})

        participant.pontos = 8
        participant.save()

        self.assertEqual(self.client.get(total_url).json(), {'total_pontos': 8})

    def test_admin_participant_list_shows_the_points_total(self):
        Participante.objects.create(nome='Ana', pontos=7)
        staff_user = get_user_model().objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='test-password',
        )
        self.client.force_login(staff_user)

        response = self.client.get(reverse('admin:placar_participante_changelist'))

        self.assertContains(response, 'Pontuação total:')
        self.assertContains(response, 'total-pontos-valor')
        self.assertContains(response, '>7</strong>')

    def test_staff_can_record_points_from_the_custom_page(self):
        participant = Participante.objects.create(nome='Ana', pontos=4)
        staff_user = get_user_model().objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='test-password',
        )
        self.client.force_login(staff_user)

        response = self.client.get(reverse('placar:gerenciar_pontos'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Lançamentos recentes')
        self.assertContains(response, 'Gerenciar pontuações')

        response = self.client.post(
            reverse('placar:gerenciar_pontos'),
            {
                'participante': participant.pk,
                'pontos': 3,
                'descricao': 'Participação na atividade',
            },
        )

        self.assertRedirects(response, reverse('placar:gerenciar_pontos'))
        participant.refresh_from_db()
        self.assertEqual(participant.pontos, 7)
        lancamento = LancamentoPontos.objects.get(participante=participant)
        self.assertEqual(lancamento.pontos, 3)
        self.assertEqual(lancamento.descricao, 'Participação na atividade')
        self.assertEqual(lancamento.administrador, staff_user)
        self.assertEqual(
            self.client.get(reverse('placar:total_pontos_json')).json(),
            {'total_pontos': 7},
        )

    def test_public_visitors_cannot_open_the_points_management_page(self):
        response = self.client.get(reverse('placar:gerenciar_pontos'))

        self.assertEqual(response.status_code, 302)
        total_response = self.client.get(reverse('placar:total_pontos_json'))
        self.assertEqual(total_response.status_code, 302)
        public_page = self.client.get(reverse('placar:inicio'))
        self.assertNotContains(public_page, 'Gerenciar pontuações')

    def test_zero_points_are_rejected_without_creating_a_history_entry(self):
        participant = Participante.objects.create(nome='Ana', pontos=4)
        staff_user = get_user_model().objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='test-password',
        )
        self.client.force_login(staff_user)

        response = self.client.post(
            reverse('placar:gerenciar_pontos'),
            {'participante': participant.pk, 'pontos': 0},
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('pontos', response.context['form'].errors)
        self.assertEqual(
            response.context['form'].errors.as_data()['pontos'][0].code,
            'min_value',
        )
        participant.refresh_from_db()
        self.assertEqual(participant.pontos, 4)
        self.assertFalse(LancamentoPontos.objects.exists())

    def test_staff_can_filter_points_history_by_participant(self):
        ana = Participante.objects.create(nome='Ana', pontos=5)
        bruna = Participante.objects.create(nome='Bruna', pontos=8)
        LancamentoPontos.objects.create(participante=ana, pontos=5)
        LancamentoPontos.objects.create(participante=bruna, pontos=8)
        staff_user = get_user_model().objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='test-password',
        )
        self.client.force_login(staff_user)

        response = self.client.get(
            reverse('placar:gerenciar_pontos'),
            {'participante': ana.pk},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Filtrar por participante')
        self.assertEqual(
            [lancamento.participante for lancamento in response.context['lancamentos']],
            [ana],
        )
        self.assertEqual(response.context['total_pontos'], 13)
