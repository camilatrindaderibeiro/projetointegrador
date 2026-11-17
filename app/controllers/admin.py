from flask import Blueprint, flash, redirect, render_template, request, url_for
from ..models import pedido
from .auth import admin_required

bp = Blueprint("admin", __name__, url_prefix="/admin")


@bp.route("/pedidos")
@admin_required
def pedidos():
    return render_template("admin_pedidos.html", pedidos=pedido.listar_todos())


@bp.route("/pedidos/<int:pedido_id>/status", methods=["POST"])
@admin_required
def atualizar_status(pedido_id):
    try:
        pedido.atualizar_status(pedido_id, request.form.get("status"))
        flash("Status atualizado.", "ok")
    except ValueError as e:
        flash(str(e), "erro")
    return redirect(url_for("admin.pedidos"))
