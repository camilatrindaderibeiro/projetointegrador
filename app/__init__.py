import os
from flask import Flask, render_template
from .db import Db, close_db, init_db


def create_app(config=None):
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-troque-em-producao"),
        DATABASE_URL=os.environ.get("DATABASE_URL", "sqlite:///cupcakeria.db"),
        SESSION_COOKIE_SAMESITE="Lax",
    )
    if config:
        app.config.update(config)

    app.teardown_appcontext(close_db)
    db = Db(app.config["DATABASE_URL"])
    try:
        init_db(db)
    finally:
        db.close()

    from .models.pedido import STATUS, PAGAMENTOS
    app.jinja_env.filters["brl"] = lambda c: f"R$ {c / 100:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    app.jinja_env.filters["status"] = lambda s: STATUS.get(s, s)
    app.jinja_env.filters["pagamento"] = lambda p: PAGAMENTOS.get(p, p)
    app.jinja_env.filters["data"] = lambda d: str(d)[:16]
    app.jinja_env.globals.update(STATUS=STATUS, PAGAMENTOS=PAGAMENTOS)

    from .controllers import auth, loja, admin
    app.register_blueprint(auth.bp)
    app.register_blueprint(loja.bp)
    app.register_blueprint(admin.bp)

    @app.errorhandler(403)
    def proibido(e):
        return render_template("erro.html", titulo="Acesso negado", msg="Você não tem permissão para esta página."), 403

    @app.errorhandler(404)
    def nao_encontrado(e):
        return render_template("erro.html", titulo="Não encontrado", msg="A página procurada não existe."), 404

    return app
