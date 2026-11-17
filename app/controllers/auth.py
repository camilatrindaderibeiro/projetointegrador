from functools import wraps
from flask import Blueprint, abort, flash, g, redirect, render_template, request, session, url_for
from ..models import usuario

bp = Blueprint("auth", __name__)


@bp.before_app_request
def carregar_usuario():
    uid = session.get("usuario_id")
    g.usuario = usuario.buscar(uid) if uid else None


def login_required(view):
    @wraps(view)
    def wrapped(*a, **kw):
        if g.usuario is None:
            flash("Faça login para continuar.", "erro")
            return redirect(url_for("auth.login", proximo=request.path))
        return view(*a, **kw)
    return wrapped


def admin_required(view):
    @wraps(view)
    @login_required
    def wrapped(*a, **kw):
        if not g.usuario["admin"]:
            abort(403)
        return view(*a, **kw)
    return wrapped


@bp.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        try:
            usuario.criar(request.form.get("nome"), request.form.get("email"), request.form.get("senha"))
        except ValueError as e:
            flash(str(e), "erro")
        else:
            flash("Cadastro realizado! Faça login.", "ok")
            return redirect(url_for("auth.login"))
    return render_template("cadastro.html")


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        u = usuario.autenticar(request.form.get("email"), request.form.get("senha"))
        if u:
            session.clear()
            session["usuario_id"] = u["id"]
            proximo = request.args.get("proximo", "")
            return redirect(proximo if proximo.startswith("/") and not proximo.startswith("//") else url_for("loja.catalogo"))
        flash("E-mail ou senha incorretos.", "erro")
    return render_template("login.html")


@bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("loja.catalogo"))
