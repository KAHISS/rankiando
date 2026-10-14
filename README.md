# Placar de pontos

Aplicação Django para cadastro de participantes, lançamento administrativo de
pontos e acompanhamento de um ranking atualizado automaticamente.

## Executar localmente

```bash
uv run python src/manage.py migrate
uv run python src/manage.py createsuperuser
uv run python src/manage.py runserver
```

Acesse [http://127.0.0.1:8000/](http://127.0.0.1:8000/) para se cadastrar e
consultar o ranking. É permitido um cadastro por navegador; essa identificação
fica salva em um cookie por até um ano. Apagar os cookies ou trocar de navegador
permite fazer outro cadastro.

Entre com o superusuário em
[http://127.0.0.1:8000/admin/login/?next=/gerenciar/](http://127.0.0.1:8000/admin/login/?next=/gerenciar/)
para abrir a área restrita de
[lançamentos de pontos](http://127.0.0.1:8000/gerenciar/). Cada lançamento guarda
a quantidade de pontos, o participante, a data, o administrador e, se informado,
o motivo. O histórico fica visível nesta tela, e a soma total atualiza
automaticamente.

## Testes

```bash
uv run python src/manage.py test placar
```