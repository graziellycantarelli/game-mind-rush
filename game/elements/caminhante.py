import pygame


class Caminhante:
    INTERVALO_TROCA = 10

    def __init__(self, caminhos_imagens, altura, pos):
        self.altura = altura
        self.pos = pygame.Vector2(pos)
        self.rota = []
        self.velocidade = 0
        self.trocar_imagens(caminhos_imagens)

    def trocar_imagens(self, caminhos_imagens):
        direita = []
        for caminho in caminhos_imagens:
            imagem = pygame.image.load(caminho).convert_alpha()
            largura = round(self.altura * imagem.get_width() / imagem.get_height())
            direita.append(pygame.transform.scale(imagem, (largura, self.altura)))
        self.imagens = {False: direita, True: [pygame.transform.flip(i, True, False) for i in direita]}
        self.virado = False
        self.frame = 0
        self.contador = 0

    @property
    def andando(self):
        return bool(self.rota)

    def ir_por(self, rota, velocidade):
        self.rota = [pygame.Vector2(p) for p in rota]
        self.velocidade = velocidade

    def atualizar(self):
        if not self.rota:
            self.frame = 0
            return

        direcao = self.rota[0] - self.pos
        if direcao.length() <= self.velocidade:
            self.pos = self.rota.pop(0)
        else:
            self.pos += direcao.normalize() * self.velocidade
            if direcao.x:
                self.virado = direcao.x < 0

        self.contador += 1
        if self.contador >= self.INTERVALO_TROCA:
            self.frame = (self.frame + 1) % len(self.imagens[False])
            self.contador = 0

    def desenhar(self, tela):
        imagem = self.imagens[self.virado][self.frame]
        tela.blit(imagem, imagem.get_rect(midbottom=self.pos))
