from flask import Blueprint, abort, flash, g, redirect, render_template, request, session, url_for
from ..models import pedido, produto
from .auth import login_required

bp = Blueprint("loja", __name__)


def _carrinho():
    return session.get("carrinho", {})


def _detalhar(carrinho):
    itens, total = [], 0
    for pid, qtd in carrinho.items():
        p = produto.buscar(int(pid))
        if p:
            sub = p["preco_centavos"] * qtd
            itens.append({"produto": p, "quantidade": qtd, "subtotal": sub})
            total += sub
    return itens, total


@bp.route("/")
def catalogo():
    return render_template("catalogo.html", produtos=produto.listar())


@bp.route("/carrinho")
def carrinho():
    itens, total = _detalhar(_carrinho())
    return render_template("carrinho.html", itens=itens, total=total)


@bp.route("/carrinho/adicionar/<int:produto_id>", methods=["POST"])
def adicionar(produto_id):
    p = produto.buscar(produto_id)
    if not p:
        abort(404)
    try:
        qtd = int(request.form.get("quantidade", 1))
    except ValueError:
        qtd = 0
    c = dict(_carrinho())
    nova = c.get(str(produto_id), 0) + qtd
    if qtd < 1:
        flash("Quantidade inválida.", "erro")
    elif nova > p["estoque"]:
        flash(f"Só temos {p['estoque']} unidade(s) de {p['nome']}.", "erro")
    else:
        c[str(produto_id)] = nova
        session["carrinho"] = c
        flash(f"{p['nome']} adicionado ao carrinho.", "ok")
    return redirect(url_for("loja.catalogo"))


@bp.route("/carrinho/remover/<int:produto_id>", methods=["POST"])
def remover(produto_id):
    c = dict(_carrinho())
    c.pop(str(produto_id), None)
    session["carrinho"] = c
    return redirect(url_for("loja.carrinho"))


@bp.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():
    itens, total = _detalhar(_carrinho())
    if not itens:
        flash("Seu carrinho está vazio.", "erro")
        return redirect(url_for("loja.catalogo"))
    if request.method == "POST":
        try:
            pid = pedido.criar(g.usuario["id"], {k: v for k, v in _carrinho().items()},
                               request.form.get("endereco"), request.form.get("pagamento"))
        except ValueError as e:
            flash(str(e), "erro")
        else:
            session.pop("carrinho", None)
            flash("Pedido realizado com sucesso!", "ok")
            return redirect(url_for("loja.detalhe_pedido", pedido_id=pid))
    return render_template("checkout.html", itens=itens, total=total)


@bp.route("/pedidos")
@login_required
def meus_pedidos():
    return render_template("pedidos.html", pedidos=pedido.listar_do_usuario(g.usuario["id"]))


@bp.route("/pedidos/<int:pedido_id>")
@login_required
def detalhe_pedido(pedido_id):
    p = pedido.buscar(pedido_id)
    if not p or (p["usuario_id"] != g.usuario["id"] and not g.usuario["admin"]):
        abort(404)
    return render_template("pedido.html", pedido=p, itens=pedido.itens(pedido_id))
