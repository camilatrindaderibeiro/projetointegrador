from ..db import get_db

STATUS = {
    "recebido": "Pedido recebido",
    "em_preparo": "Em preparo",
    "saiu_para_entrega": "Saiu para entrega",
    "entregue": "Entregue",
    "cancelado": "Cancelado",
}
PAGAMENTOS = {"pix": "Pix", "cartao": "Cartão", "dinheiro": "Dinheiro na entrega"}


def criar(usuario_id, carrinho, endereco, pagamento):
    """carrinho: {produto_id: quantidade}. Preços e total vêm SEMPRE do banco."""
    endereco = (endereco or "").strip()
    if not carrinho:
        raise ValueError("O carrinho está vazio.")
    if len(endereco) < 10:
        raise ValueError("Informe o endereço de entrega completo.")
    if pagamento not in PAGAMENTOS:
        raise ValueError("Forma de pagamento inválida.")
    db = get_db()
    linhas, total = [], 0
    for pid, qtd in carrinho.items():
        prod = db.one("SELECT * FROM produto WHERE id = ? AND ativo = 1", (int(pid),))
        if not prod:
            raise ValueError("Produto indisponível.")
        if qtd < 1:
            raise ValueError("Quantidade inválida.")
        linhas.append((prod, qtd))
        total += prod["preco_centavos"] * qtd
    pedido_id = db.insert(
        "INSERT INTO pedido (usuario_id,status,forma_pagamento,total_centavos,endereco_entrega) "
        "VALUES (?,?,?,?,?)", (usuario_id, "recebido", pagamento, total, endereco))
    for prod, qtd in linhas:
        cur = db.execute("UPDATE produto SET estoque = estoque - ? WHERE id = ? AND estoque >= ?",
                         (qtd, prod["id"], qtd))
        if cur.rowcount != 1:
            db.rollback()
            raise ValueError(f"Estoque insuficiente para {prod['nome']}.")
        db.insert("INSERT INTO item_pedido (pedido_id,produto_id,quantidade,preco_unitario_centavos) "
                  "VALUES (?,?,?,?)", (pedido_id, prod["id"], qtd, prod["preco_centavos"]))
    db.commit()
    return pedido_id


def listar_do_usuario(usuario_id):
    return get_db().all("SELECT * FROM pedido WHERE usuario_id = ? ORDER BY id DESC", (usuario_id,))


def listar_todos():
    return get_db().all("SELECT p.*, u.nome AS cliente FROM pedido p "
                        "JOIN usuario u ON u.id = p.usuario_id ORDER BY p.id DESC")


def buscar(pedido_id):
    return get_db().one("SELECT * FROM pedido WHERE id = ?", (pedido_id,))


def itens(pedido_id):
    return get_db().all("SELECT i.*, pr.nome FROM item_pedido i "
                        "JOIN produto pr ON pr.id = i.produto_id WHERE i.pedido_id = ?", (pedido_id,))


def atualizar_status(pedido_id, novo):
    if novo not in STATUS:
        raise ValueError("Status inválido.")
    db = get_db()
    if not buscar(pedido_id):
        raise ValueError("Pedido não encontrado.")
    db.execute("UPDATE pedido SET status = ? WHERE id = ?", (novo, pedido_id))
    db.commit()
