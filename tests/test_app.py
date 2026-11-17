"""Testes unitários (Model) e de integração (Controllers/Views).
Rodar: python -m unittest -v   (ou: pytest -v)"""
import os
import tempfile
import unittest

from app import create_app
from app.db import get_db
from app.models import pedido, produto, usuario


class BaseTest(unittest.TestCase):
    def setUp(self):
        fd, self.path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        self.app = create_app({"TESTING": True, "DATABASE_URL": f"sqlite:///{self.path}"})
        self.client = self.app.test_client()

    def tearDown(self):
        os.remove(self.path)

    def cadastrar_e_logar(self, email="ana@teste.com", senha="123456"):
        self.client.post("/cadastro", data={"nome": "Ana Teste", "email": email, "senha": senha})
        return self.client.post("/login", data={"email": email, "senha": senha})

    def logar_admin(self):
        return self.client.post("/login", data={"email": "admin@cupcakes.com", "senha": "admin123"})


class TestAdminInicial(unittest.TestCase):
    def test_senha_do_admin_vem_da_variavel_de_ambiente(self):
        fd, path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        os.environ["ADMIN_SENHA"] = "senha-secreta-123"
        try:
            app = create_app({"TESTING": True, "DATABASE_URL": f"sqlite:///{path}"})
            c = app.test_client()
            c.post("/login", data={"email": "admin@cupcakes.com", "senha": "admin123"})
            self.assertEqual(c.get("/admin/pedidos").status_code, 302)  # senha padrão NÃO funciona
            c.post("/login", data={"email": "admin@cupcakes.com", "senha": "senha-secreta-123"})
            self.assertEqual(c.get("/admin/pedidos").status_code, 200)
        finally:
            del os.environ["ADMIN_SENHA"]
            os.remove(path)


class TestModelUsuario(BaseTest):
    def test_cria_usuario_valido(self):
        with self.app.app_context():
            uid = usuario.criar("Ana", "ANA@teste.com", "123456")
            self.assertEqual(usuario.buscar(uid)["email"], "ana@teste.com")

    def test_rejeita_dados_invalidos(self):
        with self.app.app_context():
            for args in [("", "a@b.com", "123456"), ("Ana", "sem-arroba", "123456"), ("Ana", "a@b.com", "123")]:
                with self.assertRaises(ValueError):
                    usuario.criar(*args)

    def test_rejeita_email_duplicado(self):
        with self.app.app_context():
            usuario.criar("Ana", "a@b.com", "123456")
            with self.assertRaises(ValueError):
                usuario.criar("Outra", "a@b.com", "654321")

    def test_senha_nao_e_guardada_em_texto_puro(self):
        with self.app.app_context():
            usuario.criar("Ana", "a@b.com", "123456")
            hash_ = get_db().one("SELECT senha_hash FROM usuario WHERE email='a@b.com'")["senha_hash"]
            self.assertNotEqual(hash_, "123456")

    def test_autenticacao(self):
        with self.app.app_context():
            usuario.criar("Ana", "a@b.com", "123456")
            self.assertIsNotNone(usuario.autenticar("a@b.com", "123456"))
            self.assertIsNone(usuario.autenticar("a@b.com", "errada"))
            self.assertIsNone(usuario.autenticar("x@b.com", "123456"))


class TestModelPedido(BaseTest):
    def _usuario(self):
        return usuario.criar("Ana", "a@b.com", "123456")

    def test_cria_pedido_calcula_total_e_baixa_estoque(self):
        with self.app.app_context():
            uid, p = self._usuario(), produto.listar()[0]
            antes = p["estoque"]
            pid = pedido.criar(uid, {str(p["id"]): 2}, "Rua das Flores, 100", "pix")
            self.assertEqual(pedido.buscar(pid)["total_centavos"], 2 * p["preco_centavos"])
            self.assertEqual(produto.buscar(p["id"])["estoque"], antes - 2)
            self.assertEqual(pedido.buscar(pid)["status"], "recebido")

    def test_estoque_insuficiente_nao_cria_pedido(self):
        with self.app.app_context():
            uid, p = self._usuario(), produto.listar()[0]
            with self.assertRaises(ValueError):
                pedido.criar(uid, {str(p["id"]): p["estoque"] + 1}, "Rua das Flores, 100", "pix")
            self.assertEqual(pedido.listar_do_usuario(uid), [])
            self.assertEqual(produto.buscar(p["id"])["estoque"], p["estoque"])

    def test_validacoes(self):
        with self.app.app_context():
            uid, p = self._usuario(), produto.listar()[0]
            for args in [({}, "Rua das Flores, 100", "pix"),
                         ({str(p["id"]): 1}, "curto", "pix"),
                         ({str(p["id"]): 1}, "Rua das Flores, 100", "bitcoin"),
                         ({str(p["id"]): 0}, "Rua das Flores, 100", "pix"),
                         ({"9999": 1}, "Rua das Flores, 100", "pix")]:
                with self.assertRaises(ValueError):
                    pedido.criar(uid, *args)

    def test_atualizar_status(self):
        with self.app.app_context():
            uid, p = self._usuario(), produto.listar()[0]
            pid = pedido.criar(uid, {str(p["id"]): 1}, "Rua das Flores, 100", "cartao")
            pedido.atualizar_status(pid, "em_preparo")
            self.assertEqual(pedido.buscar(pid)["status"], "em_preparo")
            with self.assertRaises(ValueError):
                pedido.atualizar_status(pid, "inventado")
            with self.assertRaises(ValueError):
                pedido.atualizar_status(9999, "entregue")


class TestFluxoWeb(BaseTest):
    def test_catalogo_publico_com_preco_formatado(self):
        r = self.client.get("/")
        self.assertEqual(r.status_code, 200)
        self.assertIn("Red Velvet".encode(), r.data)
        self.assertIn("R$ 12,00".encode(), r.data)

    def test_pagina_inexistente_da_404(self):
        self.assertEqual(self.client.get("/nada").status_code, 404)

    def test_login_invalido_mostra_erro(self):
        r = self.client.post("/login", data={"email": "x@x.com", "senha": "zzz"})
        self.assertIn("incorretos".encode(), r.data)

    def test_checkout_exige_login(self):
        r = self.client.get("/checkout")
        self.assertEqual(r.status_code, 302)
        self.assertIn("/login", r.headers["Location"])

    def test_nao_redireciona_para_site_externo(self):
        self.cadastrar_e_logar()
        self.client.post("/logout")
        r = self.client.post("/login?proximo=//evil.com", data={"email": "ana@teste.com", "senha": "123456"})
        self.assertNotIn("evil.com", r.headers["Location"])

    def test_fluxo_completo_de_compra(self):
        self.cadastrar_e_logar()
        self.client.post("/carrinho/adicionar/1", data={"quantidade": 2})
        self.assertIn("Red Velvet".encode(), self.client.get("/carrinho").data)
        r = self.client.post("/checkout", data={"endereco": "Rua das Flores, 100", "pagamento": "pix"})
        self.assertEqual(r.status_code, 302)
        r = self.client.get(r.headers["Location"])
        self.assertIn("Pedido recebido".encode(), r.data)
        self.assertIn("R$ 24,00".encode(), r.data)
        self.assertIn("#1".encode(), self.client.get("/pedidos").data)

    def test_adicionar_acima_do_estoque_e_rejeitado(self):
        self.client.post("/carrinho/adicionar/1", data={"quantidade": 999})
        self.assertIn("vazio".encode(), self.client.get("/carrinho").data)

    def test_quantidade_nao_numerica_nao_quebra(self):
        r = self.client.post("/carrinho/adicionar/1", data={"quantidade": "abc"})
        self.assertEqual(r.status_code, 302)

    def test_remover_do_carrinho(self):
        self.client.post("/carrinho/adicionar/1", data={"quantidade": 1})
        self.client.post("/carrinho/remover/1")
        self.assertIn("vazio".encode(), self.client.get("/carrinho").data)

    def test_cliente_nao_ve_pedido_de_outro(self):
        self.cadastrar_e_logar()
        self.client.post("/carrinho/adicionar/1", data={"quantidade": 1})
        self.client.post("/checkout", data={"endereco": "Rua das Flores, 100", "pagamento": "pix"})
        self.client.post("/logout")
        self.cadastrar_e_logar("bia@teste.com")
        self.assertEqual(self.client.get("/pedidos/1").status_code, 404)

    def test_cliente_nao_acessa_area_admin(self):
        self.cadastrar_e_logar()
        self.assertEqual(self.client.get("/admin/pedidos").status_code, 403)
        self.assertEqual(self.client.post("/admin/pedidos/1/status", data={"status": "entregue"}).status_code, 403)

    def test_admin_atualiza_status_e_cliente_acompanha(self):
        self.cadastrar_e_logar()
        self.client.post("/carrinho/adicionar/1", data={"quantidade": 1})
        self.client.post("/checkout", data={"endereco": "Rua das Flores, 100", "pagamento": "pix"})
        self.client.post("/logout")
        self.logar_admin()
        self.assertEqual(self.client.get("/admin/pedidos").status_code, 200)
        self.client.post("/admin/pedidos/1/status", data={"status": "saiu_para_entrega"})
        self.client.post("/logout")
        self.client.post("/login", data={"email": "ana@teste.com", "senha": "123456"})
        self.assertIn("Saiu para entrega".encode(), self.client.get("/pedidos/1").data)


if __name__ == "__main__":
    unittest.main()
