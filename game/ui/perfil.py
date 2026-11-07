# Telas de perfil: trocar senha, trocar nome de usuário e apagar conta

import sqlite3

from game.configuracoes import LARGURA_TELA, ALTURA_TELA
from game.util.cores import cores
from game.util import validacao
from game.database import db
from game.ui.conta import (CampoTexto, TelaFormulario, desenhar_mensagem, permitido_usuario,
                            LARGURA_CAMPO, PASSO_CAMPO, COR_PERIGO)

X_CAMPOS = (LARGURA_TELA - LARGURA_CAMPO) // 2

AVISO_APAGAR = "Isso apaga a conta e as pontuações para sempre."


class TelaPerfil(TelaFormulario):
    def __init__(self):
        super().__init__()
        self.jogador = None

    def abrir(self, jogador):
        self.jogador = jogador
        self.resetar()


class TelaTrocarSenha(TelaPerfil):
    TITULO = "Trocar senha"

    def __init__(self):
        super().__init__()
        y0 = self._posicionar(3)
        self.campo_atual = CampoTexto("Senha atual", X_CAMPOS, y0, senha=True)
        self.campo_nova = CampoTexto("Nova senha", X_CAMPOS, y0 + PASSO_CAMPO, senha=True)
        self.campo_confirmar = CampoTexto("Confirmar nova senha", X_CAMPOS,
                                            y0 + 2 * PASSO_CAMPO, senha=True)
        self.campos = [self.campo_atual, self.campo_nova, self.campo_confirmar]

        self._criar_rodape("Salvar")

    def enviar(self):
        atual = self.campo_atual.texto
        nova = self.campo_nova.texto

        erro_atual = None
        if db.autenticar(self.jogador["usuario"], atual) is None:
            erro_atual = "Senha atual incorreta."

        erro_nova = validacao.validar_senha(nova)
        if not erro_nova and nova == atual:
            erro_nova = "A nova senha deve ser diferente da atual."

        erro_confirmar = validacao.validar_confirmacao(nova, self.campo_confirmar.texto)

        if self.marcar_erros([
            (self.campo_atual, erro_atual),
            (self.campo_nova, erro_nova),
            (self.campo_confirmar, erro_confirmar),
        ]):
            return None

        db.atualizar_senha(self.jogador["id"], nova)
        return "senha_alterada"


class TelaTrocarUsuario(TelaPerfil):
    TITULO = "Trocar usuário"

    def __init__(self):
        super().__init__()
        y0 = self._posicionar(2)
        self.campo_novo = CampoTexto("Novo nome de usuário", X_CAMPOS, y0,
                                    max_len=16, permitido=permitido_usuario)
        self.campo_senha = CampoTexto("Senha", X_CAMPOS, y0 + PASSO_CAMPO, senha=True)
        self.campos = [self.campo_novo, self.campo_senha]

        self._criar_rodape("Salvar")
        self.novo_usuario = ""

    def enviar(self):
        novo = self.campo_novo.texto.strip()

        erro_novo = validacao.validar_usuario(novo)
        if not erro_novo and novo == self.jogador["usuario"]:
            erro_novo = "Esse já é o seu nome de usuário."
        elif not erro_novo and db.usuario_existe(novo, ignorar_id=self.jogador["id"]):
            erro_novo = "Nome de usuário já existe. Escolha outro."

        erro_senha = None
        if db.autenticar(self.jogador["usuario"], self.campo_senha.texto) is None:
            erro_senha = "Senha incorreta."

        if self.marcar_erros([
            (self.campo_novo, erro_novo),
            (self.campo_senha, erro_senha),
        ]):
            return None

        try:
            db.atualizar_usuario(self.jogador["id"], novo)
        except sqlite3.IntegrityError:
            return self._erro("Nome de usuário já existe. Escolha outro.", self.campo_novo)

        self.novo_usuario = novo
        return "usuario_alterado"


class TelaApagarConta(TelaPerfil):
    TITULO = "Apagar conta"

    def __init__(self):
        super().__init__()
        # espaço extra entre o título e o campo, para caber o aviso
        y0 = self._posicionar(1, espaco_titulo=int(ALTURA_TELA * 0.19))
        self.campo_senha = CampoTexto("Senha para confirmar", X_CAMPOS, y0, senha=True)
        self.campos = [self.campo_senha]

        self._criar_rodape("Apagar", cor_principal=COR_PERIGO)

    def enviar(self):
        erro = None
        if db.autenticar(self.jogador["usuario"], self.campo_senha.texto) is None:
            erro = "Senha incorreta."

        if self.marcar_erros([(self.campo_senha, erro)]):
            return None

        db.apagar_jogador(self.jogador["id"])
        return "conta_apagada"

    def desenhar(self, tela, clima=None):
        super().desenhar(tela, clima)
        y_aviso = self.y_titulo + int(ALTURA_TELA * 0.065)
        desenhar_mensagem(tela, AVISO_APAGAR, cores['amarelo'], y_aviso)
