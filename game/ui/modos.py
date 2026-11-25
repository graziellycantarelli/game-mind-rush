import math

import pygame

from game.configuracoes import LARGURA_TELA, ALTURA_TELA
from game.elements.caminhante import Caminhante
from game.temas import tema
from game.ui.fontes import esc
from game.ui.seta import BotaoSeta
from game.util.cores import cores

CAMINHO_MAPA = './img/fundos/mapa_modos.png'
BORDA = 6
ALTURA_CAMINHANTE = 80
VELOCIDADE = 6

FAIXA = 6
AMPLITUDE = 2
VELOCIDADE_BALANCO = 1.8
ONDULACAO = 0.035

# coordenadas medidas na imagem original do mapa, que tem este tamanho
TAMANHO_MAPA = (1515, 833)
CRUZAMENTO = (775, 578)

# área clicável de cada ilha: (x, y, largura, altura)
ILHAS = {
    "flashcard": (150, 70, 330, 260),
    "medvet": (520, 5, 480, 285),
    "computacao": (1075, 80, 290, 255),
    "letras": (100, 390, 350, 310),
    "historia": (1000, 400, 400, 300),
}

# o centro do mapa e as ilhas ficam parados; só as árvores ao redor balançam
CENTRO = (530, 270, 460, 330)

# caminho do cruzamento até o ponto de parada de cada ilha
ROTAS = {
    "flashcard": [(700, 560), (665, 520), (630, 480), (590, 440), (555, 400), (525, 360),
                  (490, 335), (450, 315), (415, 300), (385, 290)],
    "medvet": [(850, 590), (900, 545), (950, 500), (985, 440), (990, 385), (975, 340),
               (930, 310), (880, 285), (820, 265), (745, 245)],
    "computacao": [(850, 590), (900, 545), (950, 500), (985, 440), (995, 395), (1005, 360),
                   (1030, 335), (1070, 318), (1115, 300), (1180, 305)],
    "letras": [(700, 585), (660, 545), (620, 530), (567, 515), (520, 525), (480, 550),
               (440, 580), (390, 605), (335, 605)],
    "historia": [(850, 590), (900, 545), (950, 520), (983, 521), (1030, 550), (1015, 600),
                 (1025, 660), (1050, 700), (1110, 715), (1180, 712)],
}


class TelaModos:
    def __init__(self):
        # o mapa preenche a tela toda; se as proporções diferem, sobra um corte nas bordas
        self.escala = max(LARGURA_TELA / TAMANHO_MAPA[0], ALTURA_TELA / TAMANHO_MAPA[1])
        tamanho = (round(TAMANHO_MAPA[0] * self.escala), round(TAMANHO_MAPA[1] * self.escala))
        self.mapa = pygame.transform.smoothscale(pygame.image.load(CAMINHO_MAPA).convert(), tamanho)
        self.origem = ((LARGURA_TELA - tamanho[0]) // 2, (ALTURA_TELA - tamanho[1]) // 2)

        self.amplitude = AMPLITUDE * self.escala
        self.faixas = [pygame.Rect(0, y, tamanho[0], FAIXA) for y in range(0, tamanho[1], FAIXA)]
        self.fixas = [self._no_mapa(area) for area in (*ILHAS.values(), CENTRO)]

        self.ilhas = {
            modo: pygame.Rect(*self._na_tela((x, y)), w * self.escala, h * self.escala)
            for modo, (x, y, w, h) in ILHAS.items()
        }
        self.botao_voltar = BotaoSeta("esquerda", topleft=(esc(30), esc(30)))

        self.local = None
        self.destino = None
        self.caminhante = None

    def _na_tela(self, ponto):
        return (self.origem[0] + ponto[0] * self.escala, self.origem[1] + ponto[1] * self.escala)

    def _no_mapa(self, area):
        x, y, w, h = area
        return pygame.Rect(x * self.escala, y * self.escala, w * self.escala, h * self.escala)

    def _rota_para(self, modo):
        volta = [CRUZAMENTO]
        if self.local:
            volta = [*reversed(ROTAS[self.local][:-1]), CRUZAMENTO]
        return [self._na_tela(p) for p in [*volta, *ROTAS[modo]]]

    def abrir(self, modo):
        self.local = modo
        self.destino = None
        pos = self._na_tela(ROTAS[modo][-1])
        altura = round(ALTURA_CAMINHANTE * self.escala)
        if self.caminhante is None:
            self.caminhante = Caminhante(tema(modo)["personagem"], altura, pos)
        else:
            self.caminhante.trocar_imagens(tema(modo)["personagem"])
            self.caminhante.pos = pygame.Vector2(pos)

    def _escolher(self, modo):
        self.destino = modo
        self.caminhante.trocar_imagens(tema(modo)["personagem"])
        self.caminhante.ir_por(self._rota_para(modo) if modo != self.local else [],
                               VELOCIDADE * self.escala)

    def tratar_evento(self, evento):
        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
            return "voltar"
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if self.botao_voltar.clicado(evento.pos):
                return "voltar"
            if self.destino is None:
                for modo, rect in self.ilhas.items():
                    if rect.collidepoint(evento.pos):
                        self._escolher(modo)
        return None

    def atualizar(self):
        self.caminhante.atualizar()
        if self.destino and not self.caminhante.andando:
            self.local, self.destino = self.destino, None
            return self.local
        return None

    def _desenhar_mapa(self, tela):
        tela.blit(self.mapa, self.origem)
        tempo = pygame.time.get_ticks() / 1000 * VELOCIDADE_BALANCO
        for faixa in self.faixas:
            deslocamento = round(self.amplitude * math.sin(tempo + faixa.y * ONDULACAO))
            if deslocamento:
                tela.blit(self.mapa, (self.origem[0] + deslocamento, self.origem[1] + faixa.y), faixa)
        for area in self.fixas:
            tela.blit(self.mapa, (self.origem[0] + area.x, self.origem[1] + area.y), area)

    def desenhar(self, tela):
        self._desenhar_mapa(tela)

        for modo, rect in self.ilhas.items():
            sobre = self.destino is None and rect.collidepoint(pygame.mouse.get_pos())
            if modo == self.destino or sobre:
                pygame.draw.rect(tela, cores['verde-logo'], rect, BORDA)

        self.caminhante.desenhar(tela)
        self.botao_voltar.desenhar(tela)


