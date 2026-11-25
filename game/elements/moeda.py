import pygame

COR = (255, 200, 40)
COR_BORDA = (190, 130, 20)
COR_BRILHO = (255, 238, 150)
RAIO = 22
ESPACO = 64
ALTURA_BAIXA = 100

# cada moeda:
FORMACOES = (
    ((0, 80), (1, 80), (2, 80), (3, 80)),
    ((0, 80), (1, 150), (2, 190), (3, 150), (4, 80)),
    ((0, 80), (1, 120), (2, 160), (3, 200)),
    ((0, 80), (1, 170), (2, 80), (3, 170), (4, 80)),
)


class Moeda:
    def __init__(self, x, y, deslocamento):
        self.rect = pygame.Rect(x, y, 2 * RAIO, 2 * RAIO)
        self.deslocamento = deslocamento

    def desenhar(self, tela):
        pygame.draw.circle(tela, COR, self.rect.center, RAIO)
        pygame.draw.circle(tela, COR_BORDA, self.rect.center, RAIO, 4)
        pygame.draw.circle(tela, COR_BRILHO, self.rect.center, RAIO // 2, 3)

