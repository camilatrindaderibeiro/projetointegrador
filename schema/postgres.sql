CREATE TABLE IF NOT EXISTS usuario (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    senha_hash VARCHAR(255) NOT NULL,
    admin SMALLINT NOT NULL DEFAULT 0 CHECK (admin IN (0,1)),
    criado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS produto (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(80) NOT NULL,
    descricao VARCHAR(255) NOT NULL,
    preco_centavos INTEGER NOT NULL CHECK (preco_centavos > 0),
    estoque INTEGER NOT NULL DEFAULT 0 CHECK (estoque >= 0),
    ativo SMALLINT NOT NULL DEFAULT 1 CHECK (ativo IN (0,1))
);
CREATE TABLE IF NOT EXISTS pedido (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL REFERENCES usuario(id),
    status VARCHAR(20) NOT NULL DEFAULT 'recebido'
        CHECK (status IN ('recebido','em_preparo','saiu_para_entrega','entregue','cancelado')),
    forma_pagamento VARCHAR(10) NOT NULL CHECK (forma_pagamento IN ('pix','cartao','dinheiro')),
    total_centavos INTEGER NOT NULL CHECK (total_centavos > 0),
    endereco_entrega VARCHAR(255) NOT NULL,
    criado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS item_pedido (
    id SERIAL PRIMARY KEY,
    pedido_id INTEGER NOT NULL REFERENCES pedido(id) ON DELETE CASCADE,
    produto_id INTEGER NOT NULL REFERENCES produto(id),
    quantidade INTEGER NOT NULL CHECK (quantidade > 0),
    preco_unitario_centavos INTEGER NOT NULL CHECK (preco_unitario_centavos > 0)
);
CREATE INDEX IF NOT EXISTS idx_pedido_usuario ON pedido(usuario_id);
CREATE INDEX IF NOT EXISTS idx_item_pedido ON item_pedido(pedido_id);
