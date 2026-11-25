import pygame

from game.configuracoes import LARGURA_TELA, ALTURA_TELA, imagem_bg_cadastro
from game.temas import NOMES_MODOS
from game.ui.carrossel import lugar, suavizar
from game.ui.conta import desenhar_fundo
from game.ui.estilo import COR_DICA, PALETAS, desenhar_botao_pixel
from game.ui.fontes import FontePixel, esc, renderizar
from game.ui.hud import COR_MOEDA
from game.ui.icones import desenhar_icone
from game.ui.seta import BotaoSeta

BRANCO = (255, 255, 255)
MARGEM = esc(30)
TITULO = "SEU RANKING PESSOAL"
DICA = "Setas ou roda do mouse para ver o ranking de cada modo."
POSICOES = 5

PAGINAS = ("geral", *NOMES_MODOS)
NOMES = {"geral": "GERAL", **{modo: nome.upper() for modo, nome in NOMES_MODOS.items()}}
PALETA_PAGINA = {"geral": "dourado", "flashcard": "azul", "computacao": "roxo",
                "historia": "bronze", "medvet": "verde", "letras": "vermelho"}
PALETAS_MEDALHA = ("dourado", "prata", "bronze", "azul", "roxo")

ALTURA_CARTAO = int(ALTURA_TELA * 0.62)
LARGURA_CARTAO = int(ALTURA_CARTAO * 0.80)
CENTRO_Y = int(ALTURA_TELA * 0.56)

FONTES_TITULO = (FontePixel(46), FontePixel(38), FontePixel(30))
FONTE_PAGINA = FontePixel(44)
FONTE_SUBTITULO = FontePixel(22)
FONTE_POSICAO = FontePixel(40)
FONTE_VALOR = FontePixel(40)
FONTE_DICA = FontePixel(26)


def _montar_cartao(pagina, pontos):
    """Desenha o cartão inteiro numa superfície no tamanho de foco; os outros tamanhos saem dela."""
    cartao = pygame.Surface((LARGURA_CARTAO, ALTURA_CARTAO), pygame.SRCALPHA)
    paleta = PALETAS[PALETA_PAGINA[pagina]]
    desenhar_botao_pixel(cartao, cartao.get_rect(), paleta, esc(5))
    pad = round(0.05 * LARGURA_CARTAO)

    titulo = renderizar(FONTE_PAGINA, NOMES[pagina], BRANCO, paleta[0])
    cartao.blit(titulo, titulo.get_rect(center=(LARGURA_CARTAO // 2, round(0.085 * ALTURA_CARTAO))))
    for lado in (pad + esc(14), LARGURA_CARTAO - pad - esc(14)):
        desenhar_icone(cartao, "trofeu", (lado, round(0.085 * ALTURA_CARTAO)), esc(4), BRANCO, paleta[0])
    legenda = "Suas 5 melhores partidas" if pagina == "geral" else "Suas 5 melhores neste modo"
    if not pontos:
        legenda = "Nenhuma pontuação ainda"
    subtitulo = renderizar(FONTE_SUBTITULO, legenda, paleta[3], paleta[0])
    cartao.blit(subtitulo, subtitulo.get_rect(center=(LARGURA_CARTAO // 2, round(0.165 * ALTURA_CARTAO))))

    altura_linha = round(0.115 * ALTURA_CARTAO)
    folga = round(0.022 * ALTURA_CARTAO)
    y = round(0.225 * ALTURA_CARTAO)
    for i in range(POSICOES):
        linha = pygame.Rect(pad, y + i * (altura_linha + folga), LARGURA_CARTAO - 2 * pad, altura_linha)
        _desenhar_linha(cartao, i, linha, pontos[i] if i < len(pontos) else None)
    return cartao


def _desenhar_linha(superficie, i, linha, pontos):
    medalha = PALETAS[PALETAS_MEDALHA[i]]
    numero = pygame.Rect(linha.x, linha.y, linha.height, linha.height)
    desenhar_botao_pixel(superficie, numero, medalha, esc(3))
    if i == 0:
        desenhar_icone(superficie, "coroa", (numero.centerx, numero.y + esc(14)), esc(3), BRANCO, medalha[0])
    posicao = renderizar(FONTE_POSICAO, str(i + 1), BRANCO, medalha[0])
    superficie.blit(posicao, posicao.get_rect(center=(numero.centerx, numero.centery + (esc(6) if i == 0 else -esc(3)))))

    barra = pygame.Rect(numero.right + esc(10), linha.y, linha.width - linha.height - esc(10), linha.height)
    paleta = PALETAS["dourado" if i == 0 else "azul"]
    desenhar_botao_pixel(superficie, barra, paleta, esc(3))
    desenhar_icone(superficie, "estrela", (barra.x + esc(36), barra.centery - esc(4)), esc(4), BRANCO, paleta[0])
    valor = renderizar(FONTE_VALOR, "-" if pontos is None else str(pontos), BRANCO, paleta[0])
    superficie.blit(valor, valor.get_rect(center=(barra.centerx, barra.centery - esc(4))))


class TelaRanking:
    def __init__(self):
        self.cartoes = {}
        self.indice = 0
        self.posicao = 0.0
        self.rects = {}

        self.botao_voltar = BotaoSeta("esquerda", topleft=(MARGEM, MARGEM))
        self.seta_esquerda = BotaoSeta("esquerda", centro=(esc(70), CENTRO_Y))
        self.seta_direita = BotaoSeta("direita", centro=(LARGURA_TELA - esc(70), CENTRO_Y))

    def abrir(self, dados):
        """`dados` guarda as 5 melhores pontuações de cada página."""
        self.cartoes = {pagina: _montar_cartao(pagina, dados.get(pagina) or []) for pagina in PAGINAS}
        self.indice = 0
        self.posicao = 0.0

    def _mover(self, passo):
        self.indice = min(max(0, self.indice + passo), len(PAGINAS) - 1)

    def tratar_evento(self, evento):
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                return "voltar"
            if evento.key in (pygame.K_LEFT, pygame.K_a):
                self._mover(-1)
            elif evento.key in (pygame.K_RIGHT, pygame.K_d):
                self._mover(1)
        elif evento.type == pygame.MOUSEWHEEL:
            self._mover(-evento.y)
        elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if self.botao_voltar.clicado(evento.pos):
                return "voltar"
            if self.seta_esquerda.clicado(evento.pos):
                self._mover(-1)
            elif self.seta_direita.clicado(evento.pos):
                self._mover(1)
            else:
                for indice, rect in self.rects.items():
                    if indice != self.indice and rect.collidepoint(evento.pos):
                        self.indice = indice
        return None

    def _desenhar_topo(self, tela):
        self.botao_voltar.desenhar(tela)
        paleta = PALETAS["dourado"]
        fonte = next((f for f in FONTES_TITULO if f.size(TITULO)[0] + esc(230) <= LARGURA_TELA * 0.6), FONTES_TITULO[-1])
        texto = renderizar(fonte, TITULO, BRANCO, paleta[0])
        faixa = pygame.Rect(0, 0, texto.get_width() + esc(230), esc(100))
        faixa.center = (LARGURA_TELA // 2, MARGEM + self.botao_voltar.rect.height // 2)
        desenhar_botao_pixel(tela, faixa, paleta)
        for lado in (faixa.x + esc(60), faixa.right - esc(60)):
            desenhar_icone(tela, "trofeu", (lado, faixa.centery - esc(5)), esc(5), BRANCO, paleta[0])
        tela.blit(texto, texto.get_rect(center=(faixa.centerx, faixa.centery - esc(5))))

    def _desenhar_pontos(self, tela):
        lado, folga = esc(14), esc(10)
        total = len(PAGINAS) * lado + (len(PAGINAS) - 1) * folga
        x = (LARGURA_TELA - total) // 2
        y = int(ALTURA_TELA * 0.9)
        for i in range(len(PAGINAS)):
            rect = pygame.Rect(x + i * (lado + folga), y, lado, lado)
            pygame.draw.rect(tela, COR_MOEDA if i == self.indice else PALETAS["marinho"][3], rect)
            pygame.draw.rect(tela, PALETAS["marinho"][0], rect, esc(3))

    def desenhar(self, tela, clima=None):
        desenhar_fundo(tela, imagem_bg_cadastro, clima)
        self._desenhar_topo(tela)

        self.posicao = suavizar(self.posicao, self.indice)
        self.rects = {}
        visiveis = [i for i in range(len(PAGINAS)) if abs(i - self.posicao) <= 2.6]
        for indice in sorted(visiveis, key=lambda i: -abs(i - self.posicao)):
            distancia = indice - self.posicao
            escala, deslocamento = lugar(distancia, LARGURA_CARTAO)
            base = self.cartoes[PAGINAS[indice]]
            tamanho = (round(LARGURA_CARTAO * escala), round(ALTURA_CARTAO * escala))
            cartao = base if escala == 1 else pygame.transform.smoothscale(base, tamanho)
            rect = cartao.get_rect(center=(LARGURA_TELA // 2 + round(deslocamento), CENTRO_Y))
            self.rects[indice] = rect
            tela.blit(cartao, rect)
            if indice != self.indice:
                sombra = pygame.Surface(rect.size, pygame.SRCALPHA)
                sombra.fill((0, 0, 0, min(150, round(110 * abs(distancia)))))
                tela.blit(sombra, rect)

        if self.indice > 0:
            self.seta_esquerda.desenhar(tela)
        if self.indice < len(PAGINAS) - 1:
            self.seta_direita.desenhar(tela)
        self._desenhar_pontos(tela)

        texto = renderizar(FONTE_DICA, DICA, COR_DICA)
        tela.blit(texto, texto.get_rect(midbottom=(LARGURA_TELA // 2, ALTURA_TELA - esc(24))))
