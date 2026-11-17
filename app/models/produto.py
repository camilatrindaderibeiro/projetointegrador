from ..db import get_db


def listar():
    return get_db().all("SELECT * FROM produto WHERE ativo = 1 ORDER BY nome")


def buscar(produto_id):
    return get_db().one("SELECT * FROM produto WHERE id = ? AND ativo = 1", (produto_id,))
