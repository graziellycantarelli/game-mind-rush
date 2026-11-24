import pygame
from game.configuracoes import LARGURA_TELA, ALTURA_TELA

CAMINHOS = [f"./img/logo/LOGOMR_{i}.png" for i in (1, 2, 3)]
SEQUENCIA = (0, 1, 2, 1)
INTERVALO_MS = 220


class Logo:
    def __init__(self, caminhos, centro, largura):
        imagens = [pygame.image.load(caminho) for caminho in caminhos]
        altura = round(imagens[0].get_height() * largura / imagens[0].get_width())
        self.quadros = [pygame.transform.smoothscale(imagem, (largura, altura)) for imagem in imagens]
        self.rect = self.quadros[0].get_rect(center=centro)

    def desenhar(self, tela):
        indice = SEQUENCIA[pygame.time.get_ticks() // INTERVALO_MS % len(SEQUENCIA)]
        tela.blit(self.quadros[indice], self.rect)


logo_menu = Logo(
    CAMINHOS,
    centro=(LARGURA_TELA // 2, int(ALTURA_TELA * 0.15)),
    largura=int(LARGURA_TELA * 0.4)
)
