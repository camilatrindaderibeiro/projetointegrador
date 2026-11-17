# Cupcakeria Gourmet — PIT II

Aplicação web responsiva para venda de cupcakes: cardápio, carrinho, pedido com pagamento simulado, acompanhamento de entrega e painel do gestor.

**Arquitetura MVC:** `app/models` (regras e acesso a dados) · `app/controllers` (rotas) · `app/templates` (views).
**Stack:** Python 3 + Flask · PostgreSQL (produção) / SQLite (dev e testes) · HTML + CSS.

## Rodar localmente
```bash
python -m venv venv && source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements-dev.txt
python run.py                                         # http://127.0.0.1:5000
```
Na primeira execução o banco é criado com 6 sabores e um gestor de **desenvolvimento**: `admin@cupcakes.com` / `admin123`. Em produção, defina a variável `ADMIN_SENHA` **antes do primeiro acesso** para criar o gestor com outra senha.

## Testes
```bash
python -m unittest -v      # ou: pytest -v
```

## Usar PostgreSQL
```bash
export DATABASE_URL="postgresql://usuario:senha@host:5432/cupcakeria"
export SECRET_KEY="uma-chave-longa-e-aleatoria"
export ADMIN_SENHA="uma-senha-forte"
python run.py
```
Os scripts do banco estão em `schema/` (`postgres.sql` e `sqlite.sql`); o dicionário de dados e a modelagem, em `docs/`.

## Limitações conhecidas
Pagamento simulado (sem gateway real) · sem proteção CSRF nos formulários · sem recuperação de senha · cadastro de produtos apenas via banco.

## Publicação (Render + Neon)
Comando de build: `pip install -r requirements.txt` · Comando de início: `gunicorn run:app` · Variáveis: `DATABASE_URL`, `SECRET_KEY`, `ADMIN_SENHA`, `PYTHON_VERSION=3.12.3`.
