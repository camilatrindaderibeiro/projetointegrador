"""Camada de acesso a dados: mesma API para SQLite (dev/testes) e PostgreSQL (produção).
As consultas usam '?' como parâmetro; para PostgreSQL ele é convertido em '%s'."""
import sqlite3
import os
from pathlib import Path
from flask import current_app, g
from werkzeug.security import generate_password_hash

SCHEMA_DIR = Path(__file__).resolve().parent.parent / "schema"


class Db:
    def __init__(self, url):
        self.pg = url.startswith(("postgres://", "postgresql://"))
        if self.pg:
            import psycopg2
            import psycopg2.extras
            self.conn = psycopg2.connect(url, cursor_factory=psycopg2.extras.RealDictCursor)
        else:
            self.conn = sqlite3.connect(url.replace("sqlite:///", "", 1))
            self.conn.row_factory = sqlite3.Row
            self.conn.execute("PRAGMA foreign_keys = ON")

    def execute(self, sql, params=()):
        cur = self.conn.cursor()
        cur.execute(sql.replace("?", "%s") if self.pg else sql, params)
        return cur

    def insert(self, sql, params=()):
        if self.pg:
            return self.execute(sql + " RETURNING id", params).fetchone()["id"]
        return self.execute(sql, params).lastrowid

    def one(self, sql, params=()):
        row = self.execute(sql, params).fetchone()
        return dict(row) if row else None

    def all(self, sql, params=()):
        return [dict(r) for r in self.execute(sql, params).fetchall()]

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    def close(self):
        self.conn.close()


def get_db():
    if "db" not in g:
        g.db = Db(current_app.config["DATABASE_URL"])
    return g.db


def close_db(exc=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


PRODUTOS_INICIAIS = [
    ("Red Velvet", "Massa aveludada com cobertura de cream cheese.", 1200, 30),
    ("Brigadeiro Gourmet", "Chocolate belga com cobertura de brigadeiro cremoso.", 1100, 30),
    ("Limão Siciliano", "Massa cítrica com chantilly de limão.", 1000, 25),
    ("Ninho com Morango", "Leite ninho com geleia artesanal de morango.", 1300, 20),
    ("Doce de Leite", "Recheio de doce de leite e flor de sal.", 1100, 25),
    ("Cookies and Cream", "Baunilha com pedaços de biscoito e creme.", 1250, 20),
]


def init_db(db):
    sql = (SCHEMA_DIR / ("postgres.sql" if db.pg else "sqlite.sql")).read_text(encoding="utf-8")
    if db.pg:
        db.execute(sql)
    else:
        db.conn.executescript(sql)
    if not db.one("SELECT id FROM produto"):
        for nome, desc, preco, est in PRODUTOS_INICIAIS:
            db.insert("INSERT INTO produto (nome, descricao, preco_centavos, estoque) VALUES (?,?,?,?)",
                      (nome, desc, preco, est))
    if not db.one("SELECT id FROM usuario WHERE admin = 1"):
        # Em produção defina ADMIN_SENHA. Sem ela, usa-se a senha de DESENVOLVIMENTO (admin123).
        senha = os.environ.get("ADMIN_SENHA", "admin123")
        db.insert("INSERT INTO usuario (nome,email,senha_hash,admin) VALUES (?,?,?,1)",
                  ("Administrador", "admin@cupcakes.com", generate_password_hash(senha)))
    db.commit()
