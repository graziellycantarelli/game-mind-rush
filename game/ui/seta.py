import pygame

from game.ui.estilo import PALETAS, desenhar_botao_pixel
from game.ui.fontes import esc
from game.ui.icones import desenhar_icone

LADO = esc(80)
UNIDADE_ICONE = esc(6)
BRANCO = (255, 255, 255)


class BotaoSeta:
    """Botão quadrado com uma seta: azul, e verde quando o mouse passa."""

    def __init__(self, direcao, centro=None, topleft=None, lado=LADO):
        self.icone = f"seta_{direcao}"
        self.rect = pygame.Rect(0, 0, lado, lado)
        if topleft:
            self.rect.topleft = topleft
        else:
            self.rect.center = centro

    def clicado(self, pos):
        return self.rect.collidepoint(pos)

    def desenhar(self, tela):
        paleta = PALETAS["verde" if self.rect.collidepoint(pygame.mouse.get_pos()) else "azul"]
        desenhar_botao_pixel(tela, self.rect, paleta)
        centro = (self.rect.centerx, self.rect.y + (self.rect.height - 3 * esc(4)) // 2 + esc(4))
        desenhar_icone(tela, self.icone, centro, UNIDADE_ICONE, BRANCO, paleta[0])
