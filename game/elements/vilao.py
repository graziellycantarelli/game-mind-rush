import pygame

class Vilao:
    INTERVALO_TROCA = 8

    def __init__(self, imagens, x, y_base):
        self.imagens = imagens
        largura, altura = imagens[0].get_size()
        self.rect = pygame.Rect(x, y_base - altura, largura, altura)
        self.frame_atual = 0
        self.contador_frames = 0

    @staticmethod
    def carregar_imagens(caminhos, altura):
        imagens = []
        for caminho in caminhos:
            imagem = pygame.image.load(caminho).convert_alpha()
            largura = round(altura * imagem.get_width() / imagem.get_height())
            imagem = pygame.transform.scale(imagem, (largura, altura))
            imagens.append(pygame.transform.flip(imagem, True, False))
        return imagens

    @property
    def hitbox(self):
        return self.rect.inflate(-16, -10)

    def animar(self):
        self.contador_frames += 1
        if self.contador_frames >= Vilao.INTERVALO_TROCA:
            self.frame_atual = (self.frame_atual + 1) % len(self.imagens)
            self.contador_frames = 0

    def desenhar(self, tela):
        tela.blit(self.imagens[self.frame_atual], self.rect)
