# Modelagem — Cupcakeria Gourmet

Cole cada bloco em https://mermaid.live (ou no Draw.io: Organizar → Inserir → Avançado → Mermaid) para exportar como imagem.

## Requisitos
**Funcionais:** RF01 cadastro e login · RF02 visualizar cardápio · RF03 gerenciar carrinho · RF04 finalizar pedido com endereço e pagamento · RF05 acompanhar status do pedido · RF06 gestor atualiza status dos pedidos · RF07 controle de estoque.
**Não funcionais:** RNF01 senhas com hash · RNF02 layout responsivo (celular) · RNF03 preço/total calculados no servidor · RNF04 arquitetura MVC.

## Casos de uso (descrição)
- **Cliente:** Cadastrar-se, Entrar, Ver cardápio, Gerenciar carrinho, Finalizar pedido (inclui Entrar), Acompanhar pedido.
- **Gestor (herda de Cliente):** Listar pedidos, Atualizar status.

```mermaid
flowchart LR
  C([Cliente]) --> UC1(Cadastrar-se)
  C --> UC2(Entrar)
  C --> UC3(Ver cardápio)
  C --> UC4(Gerenciar carrinho)
  C --> UC5(Finalizar pedido)
  C --> UC6(Acompanhar pedido)
  UC5 -. inclui .-> UC2
  G([Gestor]) --> UC7(Listar pedidos)
  G --> UC8(Atualizar status)
```

## Diagrama de classes (persistência)
```mermaid
classDiagram
  class Usuario { +int id +string nome +string email +string senhaHash +bool admin +datetime criadoEm }
  class Produto { +int id +string nome +string descricao +int precoCentavos +int estoque +bool ativo }
  class Pedido { +int id +string status +string formaPagamento +int totalCentavos +string enderecoEntrega +datetime criadoEm }
  class ItemPedido { +int id +int quantidade +int precoUnitarioCentavos }
  Usuario "1" --> "0..*" Pedido : realiza
  Pedido "1" *-- "1..*" ItemPedido : contém
  Produto "1" --> "0..*" ItemPedido : é vendido em
```

## Modelo entidade-relacionamento
```mermaid
erDiagram
  USUARIO ||--o{ PEDIDO : realiza
  PEDIDO ||--|{ ITEM_PEDIDO : contem
  PRODUTO ||--o{ ITEM_PEDIDO : "vendido em"
  USUARIO { int id PK string nome string email UK string senha_hash smallint admin }
  PRODUTO { int id PK string nome int preco_centavos int estoque smallint ativo }
  PEDIDO { int id PK int usuario_id FK string status string forma_pagamento int total_centavos }
  ITEM_PEDIDO { int id PK int pedido_id FK int produto_id FK int quantidade int preco_unitario_centavos }
```

## Diagrama de sequência — finalizar pedido
```mermaid
sequenceDiagram
  actor Cliente
  participant V as View (checkout.html)
  participant C as Controller (loja.checkout)
  participant M as Model (pedido.criar)
  participant DB as Banco
  Cliente->>V: informa endereço e pagamento
  V->>C: POST /checkout
  C->>M: criar(usuario, carrinho, endereco, pagamento)
  M->>DB: lê preços e valida estoque
  M->>DB: INSERT pedido + itens, UPDATE estoque
  DB-->>M: ok
  M-->>C: id do pedido
  C-->>Cliente: redireciona para /pedidos/{id}
```
