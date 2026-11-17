# Dicionário de Dados — Cupcakeria Gourmet

SGBD: PostgreSQL (produção) / SQLite (desenvolvimento e testes). Valores monetários em **centavos** (inteiro) para evitar erros de arredondamento.

## usuario
| Campo | Tipo | Restrições | Descrição |
|---|---|---|---|
| id | SERIAL | PK | Identificador |
| nome | VARCHAR(100) | NOT NULL | Nome do cliente |
| email | VARCHAR(120) | NOT NULL, UNIQUE | Login do usuário |
| senha_hash | VARCHAR(255) | NOT NULL | Hash da senha (nunca texto puro) |
| admin | SMALLINT | NOT NULL, DEFAULT 0, valores 0 ou 1 | 1 = gestor da loja |
| criado_em | TIMESTAMP | NOT NULL, DEFAULT now | Data do cadastro |

## produto
| Campo | Tipo | Restrições | Descrição |
|---|---|---|---|
| id | SERIAL | PK | Identificador |
| nome | VARCHAR(80) | NOT NULL | Sabor do cupcake |
| descricao | VARCHAR(255) | NOT NULL | Descrição exibida no cardápio |
| preco_centavos | INTEGER | NOT NULL, > 0 | Preço unitário |
| estoque | INTEGER | NOT NULL, >= 0 | Unidades disponíveis |
| ativo | SMALLINT | NOT NULL, DEFAULT 1, 0 ou 1 | 0 = oculto do cardápio |

## pedido
| Campo | Tipo | Restrições | Descrição |
|---|---|---|---|
| id | SERIAL | PK | Número do pedido |
| usuario_id | INTEGER | NOT NULL, FK → usuario.id | Cliente |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'recebido'; recebido, em_preparo, saiu_para_entrega, entregue, cancelado | Andamento da entrega |
| forma_pagamento | VARCHAR(10) | NOT NULL; pix, cartao, dinheiro | Pagamento (simulado) |
| total_centavos | INTEGER | NOT NULL, > 0 | Total calculado pelo servidor |
| endereco_entrega | VARCHAR(255) | NOT NULL | Endereço |
| criado_em | TIMESTAMP | NOT NULL, DEFAULT now | Data do pedido |

## item_pedido
| Campo | Tipo | Restrições | Descrição |
|---|---|---|---|
| id | SERIAL | PK | Identificador |
| pedido_id | INTEGER | NOT NULL, FK → pedido.id (ON DELETE CASCADE) | Pedido |
| produto_id | INTEGER | NOT NULL, FK → produto.id | Produto |
| quantidade | INTEGER | NOT NULL, > 0 | Quantidade |
| preco_unitario_centavos | INTEGER | NOT NULL, > 0 | Preço no momento da compra (histórico) |

**Relacionamentos:** usuario 1—N pedido; pedido 1—N item_pedido; produto 1—N item_pedido (relação N—N entre pedido e produto resolvida por item_pedido).
**Normalização (3FN):** sem atributos repetidos; `preco_unitario_centavos` é guardado no item de propósito, para o histórico não mudar quando o preço do produto mudar.
