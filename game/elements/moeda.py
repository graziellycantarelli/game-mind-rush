import pygame

COR = (255, 200, 40)
COR_BORDA = (190, 130, 20)
COR_BRILHO = (255, 238, 150)
RAIO = 22
ESPACO = 64          # distância entre as moedas de uma formação
ALTURA_BAIXA = 100   # formações até essa altura cabem junto de um cérebro

# cada moeda: (posição à frente, altura do centro acima do chão)
FORMACOES = (
    ((0, 80), (1, 80), (2, 80), (3, 80)),                  # linha
    ((0, 80), (1, 150), (2, 190), (3, 150), (4, 80)),      # arco
    ((0, 80), (1, 120), (2, 160), (3, 200)),               # escada
    ((0, 80), (1, 170), (2, 80), (3, 170), (4, 80)),       # zigue-zague
)


class Moeda:
    def __init__(self, x, y, deslocamento):
        self.rect = pygame.Rect(x, y, 2 * RAIO, 2 * RAIO)
        self.deslocamento = deslocamento

    def desenhar(self, tela):
        pygame.draw.circle(tela, COR, self.rect.center, RAIO)
        pygame.draw.circle(tela, COR_BORDA, self.rect.center, RAIO, 4)
        pygame.draw.circle(tela, COR_BRILHO, self.rect.center, RAIO // 2, 3)

