import pygame


class Cerebro:
    def __init__(self, imagem, x, y_base):
        self.imagem = imagem
        self.rect = imagem.get_rect(topleft=(x, y_base - imagem.get_height()))

    @staticmethod
    def carregar_imagem(altura):
        imagem = pygame.image.load('./img/elementos/cerebro.png').convert_alpha()
        largura = round(altura * imagem.get_width() / imagem.get_height())
        return pygame.transform.scale(imagem, (largura, altura))

    def desenhar(self, tela):
        tela.blit(self.imagem, self.rect)
