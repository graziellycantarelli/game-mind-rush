# Telas de conta: configurações, login e cadastro (feitas só com pygame)

import sqlite3
import pygame

from game.configuracoes import LARGURA_TELA, ALTURA_TELA, imagem_bg_cadastro
from game.util.cores import cores
from game.util import validacao
from game.database import db

# --- aparência: tudo proporcional à altura da tela (medidas pensadas para 1080p) ---
ESCALA = ALTURA_TELA / 1080
CAMINHO_FONTE = './fontes/aseprite.ttf'
FONTE_TEM_ACENTOS = False   # mude para True se trocar por uma fonte pixel que tenha acentos


def _esc(valor):
    return max(1, int(valor * ESCALA))


class FontePixel:
    """Fonte pixel do jogo; as letras com acento saem da Arial, que garante que apareçam."""

    def __init__(self, tamanho):
        self.principal = pygame.font.Font(CAMINHO_FONTE, _esc(tamanho))
        self.apoio = pygame.font.SysFont('arial', _esc(tamanho), bold=True)
        self.subida = max(self.principal.get_ascent(), self.apoio.get_ascent())
        self.descida = max(-self.principal.get_descent(), -self.apoio.get_descent())

    def _fonte_de(self, char):
        if ord(char) > 127 and not FONTE_TEM_ACENTOS:
            return self.apoio
        return self.principal

    def size(self, texto):
        largura = sum(self._fonte_de(c).size(c)[0] for c in texto)
        return largura, self.subida + self.descida

    def get_linesize(self):
        return self.subida + self.descida

    def render(self, texto, antialias, cor):
        superficie = pygame.Surface(self.size(texto), pygame.SRCALPHA)
        x = 0
        for char in texto:
            fonte = self._fonte_de(char)
            glifo = fonte.render(char, antialias, cor)
            superficie.blit(glifo, (x, self.subida - fonte.get_ascent()))
            x += glifo.get_width()
        return superficie


LARGURA_CAMPO = _esc(600)
ALTURA_CAMPO = _esc(64)
PASSO_CAMPO = _esc(112)          # distância vertical entre um campo e o próximo
ESPACO_TITULO = _esc(130)        # do centro do título ao topo do primeiro campo
LARGURA_MAX_MSG = LARGURA_CAMPO + _esc(200)
RAIO = _esc(8)
ESPESSURA_BORDA = max(2, _esc(4))
SOMBRA = max(2, _esc(3))

COR_FUNDO_CAMPO = (18, 28, 64)
COR_BORDA = (90, 120, 200)
COR_PLACEHOLDER = (110, 130, 180)
COR_TITULO = (255, 225, 60)
COR_BOTAO_NEUTRO = (255, 140, 30)
COR_PERIGO = (220, 50, 60)
COR_SAIR = (160, 90, 230)
COR_ERRO = (255, 70, 90)

FONTE_TITULO_TELA = FontePixel(72)
FONTE_ROTULO = FontePixel(30)
FONTE_CAMPO = FontePixel(34)
FONTE_MSG = FontePixel(32)
FONTE_ERRO = FontePixel(28)
FONTE_BOTAO = FontePixel(36)
FONTE_PEQUENA = FontePixel(22)

# escurece a imagem de fundo para o texto continuar legível
PELICULA = pygame.Surface((LARGURA_TELA, ALTURA_TELA))
PELICULA.set_alpha(90)


# ------------------------------------------------------------------ helpers

def permitido_usuario(char):
    return char.isascii() and (char.isalnum() or char == "_")


def _permitido_email(char):
    return not char.isspace()


def _quebrar_linhas(texto, fonte, largura_max):
    linhas, atual = [], ""
    for palavra in texto.split():
        teste = (atual + " " + palavra).strip()
        if fonte.size(teste)[0] <= largura_max:
            atual = teste
        else:
            if atual:
                linhas.append(atual)
            atual = palavra
    if atual:
        linhas.append(atual)
    return linhas


def renderizar(fonte, texto, cor):
    """Texto com sombra, como os textos do jogo."""
    frente = fonte.render(texto, True, cor)
    sombra = fonte.render(texto, True, cores['preto'])

    tamanho = (frente.get_width() + SOMBRA, frente.get_height() + SOMBRA)
    resultado = pygame.Surface(tamanho, pygame.SRCALPHA)
    resultado.blit(sombra, (SOMBRA, SOMBRA))
    resultado.blit(frente, (0, 0))
    return resultado


def desenhar_mensagem(tela, texto, cor, y_topo):
    altura_linha = FONTE_MSG.get_linesize()
    for i, linha in enumerate(_quebrar_linhas(texto, FONTE_MSG, LARGURA_MAX_MSG)):
        surf = renderizar(FONTE_MSG, linha, cor)
        tela.blit(surf, surf.get_rect(midtop=(LARGURA_TELA // 2, y_topo + i * altura_linha)))


def desenhar_fundo(tela, fundo=None, clima=None):
    if fundo:
        tela.blit(fundo, (0, 0))
        tela.blit(PELICULA, (0, 0))
        if clima:
            clima.desenhar(tela)
    else:
        tela.fill(cores['cinza-menu'])


# ------------------------------------------------------------------- campos

class CampoTexto:
    def __init__(self, rotulo, x, y, largura=LARGURA_CAMPO, altura=ALTURA_CAMPO,
                senha=False, max_len=32, permitido=None, mascara_data=False,
                placeholder="", validar=None):
        self.rotulo = rotulo
        self.rect = pygame.Rect(x, y, largura, altura)
        self.senha = senha
        self.max_len = max_len
        self.permitido = permitido
        self.mascara_data = mascara_data
        self.placeholder = placeholder
        self.validar = validar

        self.texto = ""
        self.erro = ""
        self.foco = False
        self.mostrar_senha = False

        self.rect_olho = None
        if senha:
            largura_olho = _esc(130)
            self.rect_olho = pygame.Rect(self.rect.right - largura_olho - _esc(8),
                                        self.rect.y + _esc(8), largura_olho, altura - _esc(16))

    def limpar(self):
        self.texto = ""
        self.erro = ""
        self.foco = False
        self.mostrar_senha = False

    def _esta_valido(self):
        return bool(self.texto) and self.validar is not None and not self.validar(self.texto)

    # --- entrada ---
    @staticmethod
    def _formatar_data(digitos):
        resultado = digitos[:2]
        if len(digitos) > 2:
            resultado += "/" + digitos[2:4]
        if len(digitos) > 4:
            resultado += "/" + digitos[4:]
        return resultado

    def _inserir(self, char):
        if self.mascara_data:
            if char in "0123456789":
                digitos = self.texto.replace("/", "")
                if len(digitos) < 8:
                    self.texto = self._formatar_data(digitos + char)
            return

        if len(self.texto) >= self.max_len:
            return
        if self.permitido and not self.permitido(char):
            return
        self.texto += char

    def _apagar(self):
        if self.mascara_data:
            self.texto = self._formatar_data(self.texto.replace("/", "")[:-1])
        else:
            self.texto = self.texto[:-1]

    def tratar_evento(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if self.rect_olho and self.rect_olho.collidepoint(evento.pos):
                self.mostrar_senha = not self.mostrar_senha
                self.foco = True
            else:
                self.foco = self.rect.collidepoint(evento.pos)

        elif evento.type == pygame.KEYDOWN and self.foco:
            if evento.key == pygame.K_BACKSPACE:
                self.erro = ""
                self._apagar()
            elif evento.unicode and evento.unicode.isprintable():
                self.erro = ""
                self._inserir(evento.unicode)

    # --- desenho ---
    def desenhar(self, tela):
        rotulo = renderizar(FONTE_ROTULO, self.rotulo, cores['branco'])
        tela.blit(rotulo, (self.rect.x, self.rect.y - _esc(40)))

        if self.erro:
            borda = COR_ERRO
        elif self._esta_valido():
            borda = cores['verde-logo']
        elif self.foco:
            borda = cores['amarelo']
        else:
            borda = COR_BORDA

        pygame.draw.rect(tela, COR_FUNDO_CAMPO, self.rect, border_radius=RAIO)
        pygame.draw.rect(tela, borda, self.rect, ESPESSURA_BORDA, border_radius=RAIO)

        x_texto = self.rect.x + _esc(16)
        area_largura = self.rect.width - _esc(32)
        if self.rect_olho:
            area_largura -= self.rect_olho.width + _esc(10)

        if self.senha and not self.mostrar_senha:
            exibido = "*" * len(self.texto)
        else:
            exibido = self.texto

        largura_texto = 0
        if exibido:
            surf = FONTE_CAMPO.render(exibido, True, cores['branco'])
            largura_texto = surf.get_width()
            y = self.rect.centery - surf.get_height() // 2

            if largura_texto > area_largura:
                # texto maior que o campo: mostra só o final (onde o cursor está)
                recorte = pygame.Rect(largura_texto - area_largura, 0, area_largura, surf.get_height())
                tela.blit(surf, (x_texto, y), recorte)
                largura_texto = area_largura
            else:
                tela.blit(surf, (x_texto, y))
        elif self.placeholder:
            surf = FONTE_CAMPO.render(self.placeholder, True, COR_PLACEHOLDER)
            tela.blit(surf, (x_texto, self.rect.centery - surf.get_height() // 2))

        # cursor piscando
        if self.foco and (pygame.time.get_ticks() // 500) % 2 == 0:
            x = x_texto + largura_texto + 2
            margem = _esc(12)
            pygame.draw.line(tela, cores['branco'], (x, self.rect.y + margem),
                            (x, self.rect.bottom - margem), max(2, _esc(3)))

        # botão "mostrar/ocultar" da senha
        if self.rect_olho:
            pygame.draw.rect(tela, COR_BORDA, self.rect_olho, 2, border_radius=RAIO)
            legenda = "Ocultar" if self.mostrar_senha else "Mostrar"
            surf = FONTE_PEQUENA.render(legenda, True, cores['branco'])
            tela.blit(surf, surf.get_rect(center=self.rect_olho.center))

        if self.erro:
            self._desenhar_erro(tela)

    def _desenhar_erro(self, tela):
        """Escreve o erro ao lado do campo, no espaço livre à direita."""
        x = self.rect.right + _esc(24)
        linhas = _quebrar_linhas(self.erro, FONTE_ERRO, LARGURA_TELA - x - _esc(24))
        altura_linha = FONTE_ERRO.get_linesize()
        y = self.rect.centery - len(linhas) * altura_linha // 2

        for i, linha in enumerate(linhas):
            tela.blit(renderizar(FONTE_ERRO, linha, COR_ERRO), (x, y + i * altura_linha))


class BotaoTexto:
    def __init__(self, texto, centro, largura=_esc(280), altura=_esc(70), cor=None):
        self.texto = texto
        self.cor = cor or cores['verde-logo']
        self.rect = pygame.Rect(0, 0, largura, altura)
        self.rect.center = centro

    def desenhar(self, tela):
        cor = self.cor
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            cor = tuple(min(255, c + 35) for c in cor)

        # a parte escura embaixo dá o efeito de botão em relevo
        escuro = tuple(int(c * 0.55) for c in self.cor)
        pygame.draw.rect(tela, escuro, self.rect.move(0, SOMBRA * 2), border_radius=RAIO)
        pygame.draw.rect(tela, cor, self.rect, border_radius=RAIO)

        surf = renderizar(FONTE_BOTAO, self.texto, cores['branco'])
        tela.blit(surf, surf.get_rect(center=self.rect.center))

    def clicado(self, pos):
        return self.rect.collidepoint(pos)


# ------------------------------------------------------------------- telas

class TelaConfig:
    """Menu de conta: entrar, cadastrar-se, gerenciar a conta, sair e voltar."""

    def __init__(self):
        cx = LARGURA_TELA // 2
        largura = _esc(380)
        self.y_titulo = 0
        self.mensagem = ""
        self.botao_login = BotaoTexto("Entrar", (cx, 0), largura=largura)
        self.botao_cadastro = BotaoTexto("Cadastrar-se", (cx, 0), largura=largura, cor=cores['azul-jogo'])
        self.botao_trocar_senha = BotaoTexto("Trocar senha", (cx, 0), largura=largura, cor=cores['azul-jogo'])
        self.botao_trocar_usuario = BotaoTexto("Trocar usuário", (cx, 0), largura=largura, cor=cores['azul-jogo'])
        self.botao_apagar = BotaoTexto("Apagar conta", (cx, 0), largura=largura, cor=COR_PERIGO)
        self.botao_logout = BotaoTexto("Sair da conta", (cx, 0), largura=largura, cor=COR_SAIR)
        self.botao_voltar = BotaoTexto("Voltar", (cx, 0), largura=largura, cor=COR_BOTAO_NEUTRO)

    def _botoes_ativos(self, jogador):
        if jogador:
            lista = [("trocar_senha", self.botao_trocar_senha),
                    ("trocar_usuario", self.botao_trocar_usuario),
                    ("apagar_conta", self.botao_apagar),
                    ("logout", self.botao_logout),
                    ("voltar", self.botao_voltar)]
        else:
            lista = [("login", self.botao_login),
                    ("cadastro", self.botao_cadastro),
                    ("voltar", self.botao_voltar)]

        # centraliza o conjunto (título, textos e botões) no meio da tela
        altura = _esc(301) + (len(lista) - 1) * _esc(95)
        self.y_titulo = (ALTURA_TELA - altura) // 2 + _esc(36)

        for i, (_, botao) in enumerate(lista):
            botao.rect.centery = self.y_titulo + _esc(230) + i * _esc(95)
        return lista

    def tratar_evento(self, evento, jogador):
        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
            return "voltar"

        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            for acao, botao in self._botoes_ativos(jogador):
                if botao.clicado(evento.pos):
                    return acao
        return None

    def desenhar(self, tela, jogador, clima=None):
        desenhar_fundo(tela, imagem_bg_cadastro, clima)
        botoes = self._botoes_ativos(jogador)
        cx = LARGURA_TELA // 2

        titulo = renderizar(FONTE_TITULO_TELA, "Conta", COR_TITULO)
        tela.blit(titulo, titulo.get_rect(center=(cx, self.y_titulo)))

        if jogador:
            status = f"Conectado como {jogador['usuario']}"
        else:
            status = "Você ainda não está conectado"
        surf = renderizar(FONTE_MSG, status, cores['azul-jogo'])
        tela.blit(surf, surf.get_rect(center=(cx, self.y_titulo + _esc(95))))

        if self.mensagem:
            surf = renderizar(FONTE_MSG, self.mensagem, cores['verde-logo'])
            tela.blit(surf, surf.get_rect(center=(cx, self.y_titulo + _esc(150))))

        for _, botao in botoes:
            botao.desenhar(tela)


class TelaFormulario:
    """Base de login, cadastro e telas de perfil: campos, Tab/Enter/Esc, mensagem e botões."""
    TITULO = ""
    FUNDO = None

    def __init__(self):
        self.campos = []
        self.mensagem = ""
        self.mensagem_cor = COR_ERRO
        self.y_titulo = int(ALTURA_TELA * 0.10)
        self.y_mensagem = 0
        self.botao_principal = None
        self.botao_voltar = None

    def _posicionar(self, quantidade_campos, espaco_titulo=ESPACO_TITULO):
        """Centraliza título, campos e botões no meio da tela; devolve o y do primeiro campo."""
        altura = (_esc(36) + espaco_titulo + (quantidade_campos - 1) * PASSO_CAMPO
                    + ALTURA_CAMPO + _esc(175))
        self.y_titulo = (ALTURA_TELA - altura) // 2 + _esc(36)
        return self.y_titulo + espaco_titulo

    def _criar_rodape(self, texto_principal, cor_principal=None):
        """Posiciona mensagem e botões logo abaixo do último campo."""
        cx = LARGURA_TELA // 2
        afastamento = _esc(170)
        self.y_mensagem = self.campos[-1].rect.bottom + _esc(14)
        y_botoes = self.y_mensagem + _esc(120)
        self.botao_principal = BotaoTexto(texto_principal, (cx - afastamento, y_botoes), cor=cor_principal)
        self.botao_voltar = BotaoTexto("Voltar", (cx + afastamento, y_botoes), cor=COR_BOTAO_NEUTRO)

    def definir_mensagem(self, texto, erro=True):
        self.mensagem = texto
        self.mensagem_cor = COR_ERRO if erro else cores['verde-logo']

    def marcar_erros(self, pares):
        """Recebe pares (campo, erro) e mostra cada erro ao lado do seu campo.
        Erro None significa campo ok. Retorna True se houve algum erro."""
        self.mensagem = ""
        for campo in self.campos:
            campo.erro = ""

        com_erro = [(campo, erro) for campo, erro in pares if erro]
        for campo, erro in com_erro:
            campo.erro = erro

        if com_erro:
            self.focar_campo(com_erro[0][0])
        return bool(com_erro)

    def resetar(self, mensagem=None, sucesso=False):
        for campo in self.campos:
            campo.limpar()
        self.mensagem = ""
        if mensagem:
            self.definir_mensagem(mensagem, erro=not sucesso)
        self._focar(0)

    def _focar(self, indice):
        for i, campo in enumerate(self.campos):
            campo.foco = (i == indice)

    def focar_campo(self, campo):
        self._focar(self.campos.index(campo))

    def _mover_foco(self, passo):
        atual = next((i for i, c in enumerate(self.campos) if c.foco), -1)
        self._focar((atual + passo) % len(self.campos))

    def _erro(self, texto, campo=None):
        self.definir_mensagem(texto, erro=True)
        if campo is not None:
            self._focar(self.campos.index(campo))
        return None

    def enviar(self):
        raise NotImplementedError

    def tratar_evento(self, evento):
        for campo in self.campos:
            campo.tratar_evento(evento)

        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_TAB:
                self._mover_foco(-1 if evento.mod & pygame.KMOD_SHIFT else 1)
            elif evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                return self.enviar()
            elif evento.key == pygame.K_ESCAPE:
                return "voltar"

        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if self.botao_principal.clicado(evento.pos):
                return self.enviar()
            if self.botao_voltar.clicado(evento.pos):
                return "voltar"

        return None

    def desenhar(self, tela, clima=None):
        desenhar_fundo(tela, self.FUNDO, clima)

        titulo = renderizar(FONTE_TITULO_TELA, self.TITULO, COR_TITULO)
        tela.blit(titulo, titulo.get_rect(center=(LARGURA_TELA // 2, self.y_titulo)))

        for campo in self.campos:
            campo.desenhar(tela)

        if self.mensagem:
            desenhar_mensagem(tela, self.mensagem, self.mensagem_cor, self.y_mensagem)

        self.botao_principal.desenhar(tela)
        self.botao_voltar.desenhar(tela)


class TelaLogin(TelaFormulario):
    TITULO = "Entrar"
    FUNDO = imagem_bg_cadastro

    def __init__(self):
        super().__init__()
        x = (LARGURA_TELA - LARGURA_CAMPO) // 2
        y0 = self._posicionar(2)

        self.campo_usuario = CampoTexto("Nome de usuário", x, y0,
                                        max_len=16, permitido=permitido_usuario)
        self.campo_senha = CampoTexto("Senha", x, y0 + PASSO_CAMPO, senha=True)
        self.campos = [self.campo_usuario, self.campo_senha]

        self._criar_rodape("Entrar")
        self.jogador_logado = None

    def enviar(self):
        usuario = self.campo_usuario.texto.strip()
        senha = self.campo_senha.texto

        if not usuario or not senha:
            return self._erro("Preencha o usuário e a senha.")

        jogador = db.autenticar(usuario, senha)
        if jogador is None:
            return self._erro("Usuário ou senha incorretos.", self.campo_usuario)

        self.jogador_logado = jogador
        return "logado"


class TelaCadastro(TelaFormulario):
    TITULO = "Cadastro"
    FUNDO = imagem_bg_cadastro

    def __init__(self):
        super().__init__()
        x = (LARGURA_TELA - LARGURA_CAMPO) // 2
        y0 = self._posicionar(5)

        self.campo_usuario = CampoTexto("Nome de usuário", x, y0,
                                        max_len=16, permitido=permitido_usuario,
                                        validar=validacao.validar_usuario)
        self.campo_email = CampoTexto("E-mail", x, y0 + PASSO_CAMPO,
                                        max_len=60, permitido=_permitido_email,
                                        validar=validacao.validar_email)
        self.campo_senha = CampoTexto("Senha", x, y0 + 2 * PASSO_CAMPO, senha=True,
                                        validar=validacao.validar_senha)
        self.campo_confirmar = CampoTexto("Confirmar senha", x, y0 + 3 * PASSO_CAMPO, senha=True,
                                            validar=self._validar_confirmacao)
        self.campo_nascimento = CampoTexto("Data de nascimento", x, y0 + 4 * PASSO_CAMPO,
                                            mascara_data=True, placeholder="DD/MM/AAAA",
                                            validar=self._validar_nascimento)
        self.campos = [self.campo_usuario, self.campo_email, self.campo_senha,
                        self.campo_confirmar, self.campo_nascimento]

        self._criar_rodape("Cadastrar")
        self.usuario_criado = ""

    def _validar_confirmacao(self, texto):
        return validacao.validar_confirmacao(self.campo_senha.texto, texto)

    @staticmethod
    def _validar_nascimento(texto):
        return validacao.validar_data_nascimento(texto)[0]

    def enviar(self):
        usuario = self.campo_usuario.texto.strip()
        email = self.campo_email.texto.strip()
        senha = self.campo_senha.texto
        nascimento = self.campo_nascimento.texto

        erro_usuario = validacao.validar_usuario(usuario)
        if not erro_usuario and db.usuario_existe(usuario):
            erro_usuario = "Nome de usuário já existe. Escolha outro."

        erro_email = validacao.validar_email(email)
        if not erro_email and db.email_existe(email):
            erro_email = "E-mail já cadastrado. Tente entrar com a sua conta."

        erro_senha = validacao.validar_senha(senha)
        erro_confirmar = validacao.validar_confirmacao(senha, self.campo_confirmar.texto)
        erro_nascimento, nascimento_iso = validacao.validar_data_nascimento(nascimento)

        if self.marcar_erros([
            (self.campo_usuario, erro_usuario),
            (self.campo_email, erro_email),
            (self.campo_senha, erro_senha),
            (self.campo_confirmar, erro_confirmar),
            (self.campo_nascimento, erro_nascimento),
        ]):
            return None

        try:
            db.inserir_jogador(usuario, email, senha, nascimento_iso)
        except sqlite3.IntegrityError:
            return self._erro("Usuário ou e-mail já cadastrado. Tente outros dados.", self.campo_usuario)

        self.usuario_criado = usuario
        return "cadastrado"
