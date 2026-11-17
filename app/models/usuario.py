from werkzeug.security import check_password_hash, generate_password_hash
from ..db import get_db


def criar(nome, email, senha):
    nome = (nome or "").strip()
    email = (email or "").strip().lower()
    if not nome:
        raise ValueError("Informe o nome.")
    if "@" not in email or "." not in email.split("@")[-1]:
        raise ValueError("E-mail inválido.")
    if len(senha or "") < 6:
        raise ValueError("A senha deve ter ao menos 6 caracteres.")
    db = get_db()
    if db.one("SELECT id FROM usuario WHERE email = ?", (email,)):
        raise ValueError("E-mail já cadastrado.")
    uid = db.insert("INSERT INTO usuario (nome,email,senha_hash,admin) VALUES (?,?,?,0)",
                    (nome, email, generate_password_hash(senha)))
    db.commit()
    return uid


def autenticar(email, senha):
    u = get_db().one("SELECT * FROM usuario WHERE email = ?", ((email or "").strip().lower(),))
    if u and check_password_hash(u["senha_hash"], senha or ""):
        return u
    return None


def buscar(usuario_id):
    return get_db().one("SELECT id, nome, email, admin FROM usuario WHERE id = ?", (usuario_id,))
