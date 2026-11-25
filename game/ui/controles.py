import pygame

from game.configuracoes import LARGURA_TELA, ALTURA_TELA
from game.ui.estilo import PALETAS, desenhar_botao_pixel
from game.ui.fontes import esc
from game.ui.icones import desenhar_icone

LADO = esc(76)
MARGEM = esc(20)
ESPACO = esc(12)
UNIDADE_ICONE = esc(6)
BRANCO = (255, 255, 255)
COR_DESLIGADO = (255, 70, 90)

# ação, ícone
BOTOES = (("pausar", "pausa"), ("efeitos", "som"), ("musica", "musica"))


class BotoesJogo:
    """Pausar, ligar/desligar os efeitos e ligar/desligar a música, no canto da tela durante a partida."""

    def __init__(self):
        x = LARGURA_TELA - MARGEM - len(BOTOES) * LADO - (len(BOTOES) - 1) * ESPACO
        y = ALTURA_TELA - MARGEM - LADO
        self.rects = [pygame.Rect(x + i * (LADO + ESPACO), y, LADO, LADO) for i in range(len(BOTOES))]

    def clique(self, pos):
        for rect, (acao, _) in zip(self.rects, BOTOES):
            if rect.collidepoint(pos):
                return acao
        return None

    def desenhar(self, tela, som):
        ligados = (True, som.efeitos_ligados, som.musica_ligada)
        mouse = pygame.mouse.get_pos()
        for rect, (_, icone), ligado in zip(self.rects, BOTOES, ligados):
            paleta = PALETAS["verde" if rect.collidepoint(mouse) else "azul"]
            desenhar_botao_pixel(tela, rect, paleta)
            centro = (rect.centerx, rect.y + (rect.height - 3 * esc(4)) // 2 + esc(4))
            desenhar_icone(tela, icone, centro, UNIDADE_ICONE, BRANCO, paleta[0])
            if not ligado:
                metade = 3 * UNIDADE_ICONE
                for desvio, cor in ((esc(3), paleta[0]), (0, COR_DESLIGADO)):
                    pygame.draw.line(tela, cor, (centro[0] - metade + desvio, centro[1] - metade + desvio),
                                    (centro[0] + metade + desvio, centro[1] + metade + desvio), esc(8))
