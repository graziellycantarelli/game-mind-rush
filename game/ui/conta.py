# Telas de conta: configurações, login e cadastro (feitas só com pygame)

import sqlite3
import pygame

from game.configuracoes import LARGURA_TELA, ALTURA_TELA, imagem_bg_cadastro
from game.util.cores import cores
from game.util import validacao
from game.database import db
from game.ui.estilo import (COR_TITULO, COR_CREME, COR_TINTA, COR_ERRO, COR_ERRO_TEXTO, COR_SUCESSO_TEXTO,
                            COR_MADEIRA, COR_MADEIRA_ESCURA, COR_PAPEL, PALETAS, clarear, escurecer,
                            desenhar_bloco_pixel, desenhar_botao_pixel)
from game.ui.fontes import FontePixel, arial, esc as _esc, renderizar
from game.ui.icones import desenhar_icone

LARGURA_CAMPO = _esc(600)
ALTURA_CAMPO = _esc(64)
PASSO_CAMPO = _esc(112)          # distância vertical entre um campo e o próximo
ESPACO_TITULO = _esc(130)        # do centro do título ao topo do primeiro campo
LARGURA_MAX_MSG = LARGURA_CAMPO + _esc(200)

COR_PLACEHOLDER = (160, 135, 105)
COR_SELECAO = (90, 160, 240, 120)
COR_BALAO = (100, 24, 36)
COR_BOTAO_NEUTRO = (255, 140, 30)
COR_PERIGO = (220, 50, 60)
COR_SAIR = (160, 90, 230)
PALETA_POR_COR = {tuple(cores['azul-jogo']): "azul", COR_PERIGO: "vermelho", COR_SAIR: "roxo", COR_BOTAO_NEUTRO: "dourado"}
BRANCO = (255, 255, 255)

# título em fonte pixel; o resto usa a mesma fonte das perguntas
FONTES_TITULO_TELA = (FontePixel(72), FontePixel(56), FontePixel(44))
FONTE_TITULO_TELA = FONTES_TITULO_TELA[0]
FONTE_NOME_PERFIL = FontePixel(44)
FONTE_ROTULO = arial(30)
FONTE_CAMPO = arial(34)
FONTE_MSG = arial(32)
FONTE_ERRO = arial(28)
FONTE_BOTAO = FontePixel(34)
FONTE_PEQUENA = arial(22)


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


def desenhar_mensagem(tela, texto, cor, y_topo):
    altura_linha = FONTE_MSG.get_linesize()
    for i, linha in enumerate(_quebrar_linhas(texto, FONTE_MSG, LARGURA_MAX_MSG)):
        surf = renderizar(FONTE_MSG, linha, cor)
        tela.blit(surf, surf.get_rect(midtop=(LARGURA_TELA // 2, y_topo + i * altura_linha)))


def desenhar_fundo(tela, fundo=None, clima=None):
    if fundo:
        tela.blit(fundo, (0, 0))
        if clima:
            clima.desenhar(tela)
    else:
        tela.fill(cores['cinza-menu'])


def desenhar_painel(tela, rect):
    desenhar_bloco_pixel(tela, rect, COR_MADEIRA, COR_MADEIRA_ESCURA, canto=_esc(10), espessura=_esc(8), sombra=_esc(10))


def desenhar_cabecalho(tela, titulo, icone, centro_x, centro_y, largura_maxima):
    """Faixa dourada com o título e um ícone de cada lado, sobre a borda de cima do painel."""
    paleta = PALETAS["dourado"]
    fonte = next((f for f in FONTES_TITULO_TELA if f.size(titulo.upper())[0] + _esc(230) <= largura_maxima),
                 FONTES_TITULO_TELA[-1])
    texto = renderizar(fonte, titulo.upper(), BRANCO, paleta[0])
    faixa = pygame.Rect(0, 0, texto.get_width() + _esc(230), _esc(120))
    faixa.center = (centro_x, centro_y)
    desenhar_botao_pixel(tela, faixa, paleta)
    for lado in (faixa.x + _esc(70), faixa.right - _esc(70)):
        desenhar_icone(tela, icone, (lado, faixa.centery - _esc(6)), _esc(6), BRANCO, paleta[0])
    tela.blit(texto, texto.get_rect(center=(centro_x, faixa.centery - _esc(6))))


def _icone_do_rotulo(rotulo):
    nome = rotulo.lower()
    for palavra, icone in (("usuário", "usuario"), ("senha", "cadeado"), ("e-mail", "email"), ("nascimento", "calendario")):
        if palavra in nome:
            return icone
    return None


# ------------------------------------------------------------------- campos

class CampoTexto:
    """Campo de texto com cursor, seleção (teclado, arrastar e duplo clique) e edição no meio do texto."""

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

        self.erro = ""
        self.foco = False
        self.mostrar_senha = False
        self.ancora = None            # ponto onde a seleção começou (None = sem seleção)
        self.rolagem = 0
        self.arrastando = False
        self.ultimo_clique = 0
        self.texto = ""

        self.rect_olho = None
        if senha:
            largura_olho = _esc(130)
            self.rect_olho = pygame.Rect(self.rect.right - largura_olho - _esc(8),
                                        self.rect.y + _esc(8), largura_olho, altura - _esc(16))

    @property
    def texto(self):
        return self._texto

    @texto.setter
    def texto(self, valor):
        self._texto = valor
        self.cursor = len(valor)
        self.ancora = None

    def limpar(self):
        self.texto = ""
        self.erro = ""
        self.foco = False
        self.mostrar_senha = False
        self.rolagem = 0
        self.arrastando = False

    def _esta_valido(self):
        return bool(self.texto) and self.validar is not None and not self.validar(self.texto)

    # --- edição ---
    @staticmethod
    def _formatar_data(digitos):
        resultado = digitos[:2]
        if len(digitos) > 2:
            resultado += "/" + digitos[2:4]
        if len(digitos) > 4:
            resultado += "/" + digitos[4:]
        return resultado

    @staticmethod
    def _digitos(texto):
        return "".join(c for c in texto if c.isdigit())

    @staticmethod
    def _indice_data(quantidade):
        """Posição do cursor na data formatada depois de N dígitos."""
        return quantidade + (quantidade > 2) + (quantidade > 4)

    def _faixa(self):
        if self.ancora is None:
            return self.cursor, self.cursor
        return min(self.ancora, self.cursor), max(self.ancora, self.cursor)

    def _substituir(self, ini, fim, novo):
        """Troca texto[ini:fim] por `novo` e deixa o cursor logo depois."""
        if self.mascara_data:
            antes = self._digitos(self._texto[:ini])
            depois = self._digitos(self._texto[fim:])
            self._texto = self._formatar_data((antes + novo + depois)[:8])
            self.cursor = self._indice_data(min(len(antes) + len(novo), 8))
        else:
            livre = self.max_len - (len(self._texto) - (fim - ini))
            novo = novo[:max(0, livre)]
            self._texto = self._texto[:ini] + novo + self._texto[fim:]
            self.cursor = ini + len(novo)
        self.ancora = None

    def _inserir(self, char):
        ini, fim = self._faixa()
        if self.mascara_data:
            if char not in "0123456789":
                return
            if len(self._digitos(self._texto)) - len(self._digitos(self._texto[ini:fim])) >= 8:
                return
        elif self.permitido and not self.permitido(char):
            return
        self._substituir(ini, fim, char)

    def _apagar(self, para_tras):
        ini, fim = self._faixa()
        if ini == fim:
            if para_tras:
                ini = max(0, ini - (2 if self.mascara_data and self._texto[ini - 1:ini] == "/" else 1))
            else:
                fim = min(len(self._texto), fim + (2 if self.mascara_data and self._texto[fim:fim + 1] == "/" else 1))
        self._substituir(ini, fim, "")

    def _mover(self, destino, selecionar):
        if selecionar:
            if self.ancora is None:
                self.ancora = self.cursor
        else:
            self.ancora = None
        self.cursor = max(0, min(len(self._texto), destino))

    def _tecla(self, evento):
        shift = evento.mod & pygame.KMOD_SHIFT
        ctrl = evento.mod & pygame.KMOD_CTRL and not evento.mod & pygame.KMOD_ALT   # AltGr não conta
        ini, fim = self._faixa()
        tecla = evento.key

        if tecla == pygame.K_BACKSPACE:
            self.erro = ""
            self._apagar(True)
        elif tecla == pygame.K_DELETE:
            self.erro = ""
            self._apagar(False)
        elif tecla == pygame.K_LEFT:
            self._mover(ini if ini != fim and not shift else self.cursor - 1, shift)
        elif tecla == pygame.K_RIGHT:
            self._mover(fim if ini != fim and not shift else self.cursor + 1, shift)
        elif tecla == pygame.K_HOME:
            self._mover(0, shift)
        elif tecla == pygame.K_END:
            self._mover(len(self._texto), shift)
        elif ctrl and tecla == pygame.K_a:
            self.ancora = 0
            self.cursor = len(self._texto)
        elif not ctrl and evento.unicode and evento.unicode.isprintable():
            self.erro = ""
            self._inserir(evento.unicode)

    # --- posição do texto na tela ---
    def _exibido(self):
        return "*" * len(self._texto) if self.senha and not self.mostrar_senha else self._texto

    def _x_ate(self, indice):
        return FONTE_CAMPO.size(self._exibido()[:indice])[0]

    def _indice_em(self, x):
        """Índice do caractere mais próximo de x, em pixels a partir do começo do texto."""
        exibido = self._exibido()
        for i in range(len(exibido)):
            meio = (FONTE_CAMPO.size(exibido[:i])[0] + FONTE_CAMPO.size(exibido[:i + 1])[0]) / 2
            if x < meio:
                return i
        return len(exibido)

    def _area_texto(self):
        largura = self.rect.width - _esc(32)
        if self.rect_olho:
            largura -= self.rect_olho.width + _esc(10)
        return pygame.Rect(self.rect.x + _esc(16), self.rect.y, largura, self.rect.height)

    # --- eventos ---
    def tratar_evento(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if self.rect_olho and self.rect_olho.collidepoint(evento.pos):
                self.mostrar_senha = not self.mostrar_senha
                self.foco = True
            elif self.rect.collidepoint(evento.pos):
                agora = pygame.time.get_ticks()
                self.foco = True
                if agora - self.ultimo_clique < 400:
                    self.ancora = 0
                    self.cursor = len(self._texto)
                else:
                    self.cursor = self._indice_em(evento.pos[0] - self._area_texto().x + self.rolagem)
                    self.ancora = self.cursor
                    self.arrastando = True
                self.ultimo_clique = agora
            else:
                self.foco = False

        elif evento.type == pygame.MOUSEMOTION and self.arrastando:
            self.cursor = self._indice_em(evento.pos[0] - self._area_texto().x + self.rolagem)

        elif evento.type == pygame.MOUSEBUTTONUP and evento.button == 1:
            self.arrastando = False

        elif evento.type == pygame.KEYDOWN and self.foco:
            self._tecla(evento)

    # --- desenho ---
    def desenhar(self, tela):
        valido = self._esta_valido()
        y_rotulo = self.rect.y - _esc(40)
        x_rotulo = self.rect.x
        icone = _icone_do_rotulo(self.rotulo)
        if icone:
            desenhar_icone(tela, icone, (self.rect.x + _esc(14), y_rotulo + _esc(17)), _esc(3), COR_TITULO, COR_MADEIRA_ESCURA)
            x_rotulo += _esc(40)
        tela.blit(renderizar(FONTE_ROTULO, self.rotulo, COR_CREME), (x_rotulo, y_rotulo))
        if valido:
            desenhar_icone(tela, "check", (self.rect.right - _esc(16), y_rotulo + _esc(17)), _esc(3),
                           cores['verde-logo'], COR_MADEIRA_ESCURA)

        if self.erro:
            borda = COR_ERRO
        elif valido:
            borda = cores['verde-logo']
        elif self.foco:
            borda = PALETAS["azul"][1]
        else:
            borda = COR_MADEIRA_ESCURA
        desenhar_bloco_pixel(tela, self.rect, COR_PAPEL, borda, canto=_esc(4), espessura=_esc(4), sombra=0)

        area = self._area_texto()
        x_cursor = self._x_ate(self.cursor)
        if x_cursor - self.rolagem > area.width:
            self.rolagem = x_cursor - area.width
        if x_cursor - self.rolagem < 0:
            self.rolagem = x_cursor

        exibido = self._exibido()
        margem = _esc(12)
        tela.set_clip(area.inflate(_esc(6), 0))

        ini, fim = self._faixa()
        if ini != fim and self.foco:
            x1 = area.x + self._x_ate(ini) - self.rolagem
            x2 = area.x + self._x_ate(fim) - self.rolagem
            selecao = pygame.Surface((max(1, x2 - x1), self.rect.height - 2 * margem), pygame.SRCALPHA)
            selecao.fill(COR_SELECAO)
            tela.blit(selecao, (x1, self.rect.y + margem))

        if exibido:
            surf = FONTE_CAMPO.render(exibido, True, COR_TINTA)
            tela.blit(surf, (area.x - self.rolagem, self.rect.centery - surf.get_height() // 2))
        elif self.placeholder:
            surf = FONTE_CAMPO.render(self.placeholder, True, COR_PLACEHOLDER)
            tela.blit(surf, (area.x, self.rect.centery - surf.get_height() // 2))

        if self.foco and (pygame.time.get_ticks() // 500) % 2 == 0:
            x = area.x + x_cursor - self.rolagem
            pygame.draw.line(tela, COR_TINTA, (x, self.rect.y + margem),
                            (x, self.rect.bottom - margem), max(2, _esc(3)))
        tela.set_clip(None)

        # botão "mostrar/ocultar" da senha
        if self.rect_olho:
            paleta = PALETAS["verde" if self.rect_olho.collidepoint(pygame.mouse.get_pos()) else "azul"]
            desenhar_botao_pixel(tela, self.rect_olho, paleta, _esc(3))
            legenda = "Ocultar" if self.mostrar_senha else "Mostrar"
            surf = renderizar(FONTE_PEQUENA, legenda, BRANCO, paleta[0])
            tela.blit(surf, surf.get_rect(center=(self.rect_olho.centerx, self.rect_olho.centery - _esc(3))))

        if self.erro:
            self._desenhar_erro(tela)

    def _desenhar_erro(self, tela):
        """Balão com o erro, ao lado do campo, no espaço livre à direita."""
        folga = _esc(12)
        x = self.rect.right + _esc(40)
        linhas = _quebrar_linhas(self.erro, FONTE_ERRO, LARGURA_TELA - x - _esc(60))
        altura_linha = FONTE_ERRO.get_linesize()
        largura = max(FONTE_ERRO.size(linha)[0] for linha in linhas) + 2 * folga
        altura = len(linhas) * altura_linha + 2 * folga
        balao = pygame.Rect(x, self.rect.centery - altura // 2, largura, altura)

        desenhar_bloco_pixel(tela, balao, COR_BALAO, COR_ERRO, canto=_esc(3), espessura=_esc(3), sombra=0)
        centro = balao.centery
        pygame.draw.polygon(tela, COR_BALAO, [(balao.x - folga, centro), (balao.x, centro - folga // 2),
                                            (balao.x, centro + folga // 2)])
        for i, linha in enumerate(linhas):
            tela.blit(FONTE_ERRO.render(linha, True, COR_ERRO_TEXTO),
                      (balao.x + folga, balao.y + folga + i * altura_linha))


def _paleta_do_botao(cor):
    nome = PALETA_POR_COR.get(tuple(cor)) if cor else "azul"
    if nome:
        return PALETAS[nome], nome == "azul"
    return (escurecer(cor, 0.3), cor, escurecer(cor, 0.75), clarear(cor, 70)), False


class BotaoTexto:
    """Botão pixelado: azul vira verde quando o mouse passa; os demais só clareiam."""

    def __init__(self, texto, centro, largura=_esc(280), altura=_esc(70), cor=None, fonte=None):
        self.texto = texto
        self.paleta, self.vira_verde = _paleta_do_botao(cor)
        self.fonte = fonte or FONTE_BOTAO
        self.rect = pygame.Rect(0, 0, largura, altura)
        self.rect.center = centro

    def desenhar(self, tela):
        paleta = self.paleta
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            paleta = PALETAS["verde"] if self.vira_verde else tuple(clarear(c, 25) for c in paleta)
        desenhar_botao_pixel(tela, self.rect, paleta)

        surf = renderizar(self.fonte, self.texto, BRANCO, paleta[0])
        centro = (self.rect.centerx, self.rect.y + (self.rect.height - _esc(12)) // 2 + _esc(4))
        tela.blit(surf, surf.get_rect(center=centro))

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
        altura = _esc(401) + (len(lista) - 1) * _esc(95)
        self.y_titulo = (ALTURA_TELA - altura) // 2 + _esc(36)

        for i, (_, botao) in enumerate(lista):
            botao.rect.centery = self.y_titulo + _esc(330) + i * _esc(95)
        return lista

    def tratar_evento(self, evento, jogador):
        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
            return "voltar"

        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            for acao, botao in self._botoes_ativos(jogador):
                if botao.clicado(evento.pos):
                    return acao
        return None

    def _desenhar_perfil(self, tela, jogador, cx):
        """Cartão com o avatar, o nome do jogador e se ele está conectado."""
        lado = _esc(120)
        nome = renderizar(FONTE_NOME_PERFIL, jogador["usuario"] if jogador else "Visitante", COR_TITULO)
        status = renderizar(FONTE_MSG, "Conectado" if jogador else "Você ainda não está conectado", COR_CREME)
        largura_texto = max(nome.get_width(), status.get_width())
        centro_y = self.y_titulo + _esc(130)

        avatar = pygame.Rect(cx - (lado + _esc(30) + largura_texto) // 2, centro_y - lado // 2, lado, lado)
        paleta = PALETAS["azul" if jogador else "prata"]
        desenhar_botao_pixel(tela, avatar, paleta)
        desenhar_icone(tela, "usuario", (avatar.centerx, avatar.centery - _esc(6)), _esc(9), BRANCO, paleta[0])
        tela.blit(nome, (avatar.right + _esc(30), centro_y - nome.get_height()))
        tela.blit(status, (avatar.right + _esc(30), centro_y + _esc(4)))

    def desenhar(self, tela, jogador, clima=None):
        desenhar_fundo(tela, imagem_bg_cadastro, clima)
        botoes = self._botoes_ativos(jogador)
        cx = LARGURA_TELA // 2

        largura = _esc(780)
        base = botoes[-1][1].rect.bottom + _esc(60)
        desenhar_painel(tela, pygame.Rect(cx - largura // 2, self.y_titulo, largura, base - self.y_titulo))
        desenhar_cabecalho(tela, "Conta", "usuario", cx, self.y_titulo, largura - _esc(30))
        self._desenhar_perfil(tela, jogador, cx)

        altura_linha = FONTE_ERRO.get_linesize()
        for i, linha in enumerate(_quebrar_linhas(self.mensagem, FONTE_ERRO, largura - _esc(60))):
            surf = renderizar(FONTE_ERRO, linha, COR_SUCESSO_TEXTO)
            tela.blit(surf, surf.get_rect(midtop=(cx, self.y_titulo + _esc(222) + i * altura_linha)))

        for _, botao in botoes:
            botao.desenhar(tela)


class TelaFormulario:
    """Base de login, cadastro e telas de perfil: campos, Tab/Enter/Esc, mensagem e botões."""
    TITULO = ""
    ICONE = "usuario"
    FUNDO = None

    def __init__(self):
        self.campos = []
        self.mensagem = ""
        self.mensagem_cor = COR_ERRO_TEXTO
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
        self.mensagem_cor = COR_ERRO_TEXTO if erro else COR_SUCESSO_TEXTO

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

        base = self.botao_principal.rect.bottom + _esc(60)
        largura = LARGURA_CAMPO + _esc(220)
        desenhar_painel(tela, pygame.Rect((LARGURA_TELA - largura) // 2, self.y_titulo, largura, base - self.y_titulo))
        desenhar_cabecalho(tela, self.TITULO, self.ICONE, LARGURA_TELA // 2, self.y_titulo, largura - _esc(30))

        for campo in self.campos:
            campo.desenhar(tela)

        if self.mensagem:
            desenhar_mensagem(tela, self.mensagem, self.mensagem_cor, self.y_mensagem)

        self.botao_principal.desenhar(tela)
        self.botao_voltar.desenhar(tela)


class TelaLogin(TelaFormulario):
    TITULO = "Entrar"
    ICONE = "cadeado"
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
    ICONE = "estrela"
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

