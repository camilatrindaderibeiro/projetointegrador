# Cupcakeria Gourmet — PIT II

Aplicação web responsiva para venda de cupcakes: cardápio, carrinho, pedido com pagamento simulado, acompanhamento de entrega e painel do gestor.

**Arquitetura MVC:** `app/models` (regras e acesso a dados) · `app/controllers` (rotas) · `app/templates` (views).
**Stack:** Python 3 + Flask · PostgreSQL (produção) / SQLite (dev e testes) · HTML + CSS.

## Rodar localmente
```bash
python -m venv venv && source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
python run.py                                         # http://127.0.0.1:5000
```
Na primeira execução o banco é criado com 6 sabores e um gestor de **desenvolvimento**: `admin@cupcakes.com` / `admin123`. **Troque essa senha antes de publicar.**

## Testes
```bash
python -m unittest -v      # ou: pytest -v
```

## Usar PostgreSQL
```bash
export DATABASE_URL="postgresql://usuario:senha@host:5432/cupcakeria"
export SECRET_KEY="uma-chave-longa-e-aleatoria"
python run.py
```
Os scripts do banco estão em `schema/` (`postgres.sql` e `sqlite.sql`); o dicionário de dados e a modelagem, em `docs/`.

## Limitações conhecidas
Pagamento simulado (sem gateway real) · sem proteção CSRF nos formulários · sem recuperação de senha · cadastro de produtos apenas via banco.
