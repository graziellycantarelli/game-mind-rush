import pygame

from game.util.cores import cores

FRAMES_IMUNIDADE = 60


class Personagem:
    def __init__(self, largura_tela, altura_tela, x, y, altura, caminhos_imagens):
        self.largura_tela = largura_tela
        self.altura_tela = altura_tela

        self.rect = pygame.Rect(x, y, 0, altura)

        #física vertical
        # pos_y guarda a posição como float: o Rect só aceita inteiros, e
        # somar 0.6 direto no rect.y fazia o personagem "piscar" no chão
        # (no_chao alternava True/False e o pulo falhava a cada 2 frames)
        self.pos_y = float(y)
        self.bottom_anterior = self.rect.bottom
        self.velocidade_y = 0
        self.gravidade = 0.9
        self.forca_salto = -22

        #controle de estado
        self.no_chao = False
        self.vivo = True

        #power-ups
        self.escudo = False
        self.pulo_duplo = False
        self.pulos_no_ar = 0
        self.imune = 0

        self.intervalo_troca = 8
        self.trocar_imagens(caminhos_imagens, altura)

    def trocar_imagens(self, caminhos_imagens, altura):
        """Carrega os quadros de corrida; a largura segue a proporção da imagem."""
        imagens = []
        for caminho in caminhos_imagens:
            imagem = pygame.image.load(caminho).convert_alpha()
            largura = round(altura * imagem.get_width() / imagem.get_height())
            imagens.append(pygame.transform.scale(imagem, (largura, altura)))

        self.imagens = imagens
        self.altura = altura
        self.largura = imagens[0].get_width()
        self.rect.size = (self.largura, self.altura)
        self.frame_atual = 0
        self.contador_frames = 0

    @property
    def hitbox(self):
        return self.rect.inflate(-20, -10)

    def resetar(self, x, y):
        self.rect.x = x
        self.rect.y = y
        self.pos_y = float(y)
        self.bottom_anterior = self.rect.bottom
        self.velocidade_y = 0
        self.no_chao = False
        self.vivo = True
        self.escudo = False
        self.pulo_duplo = False
        self.pulos_no_ar = 0
        self.imune = 0
        self.frame_atual = 0
        self.contador_frames = 0

    def pular(self):
        if self.no_chao:
            self.velocidade_y = self.forca_salto
            self.no_chao = False
        elif self.pulo_duplo and self.pulos_no_ar < 1:
            self.velocidade_y = self.forca_salto
            self.pulos_no_ar += 1

    def aplicar_gravidade(self):
        self.bottom_anterior = self.rect.bottom

        self.velocidade_y += self.gravidade
        self.pos_y += self.velocidade_y
        self.rect.y = round(self.pos_y)

    def verificar_colisao_com_chao(self, lista_de_chaos):
        self.no_chao = False

        for chao in lista_de_chaos:
            if not self.rect.colliderect(chao.rect):
                continue

            if self.velocidade_y >= 0 and self.bottom_anterior <= chao.rect.top + 10:
                self.rect.bottom = chao.rect.top
                self.pos_y = float(self.rect.y)
                self.velocidade_y = 0
                self.no_chao = True
                self.pulos_no_ar = 0
                break

            if self.hitbox.colliderect(chao.rect) and self._ferir():
                self.rect.bottom = chao.rect.top
                self.pos_y = float(self.rect.y)
                self.velocidade_y = 0
                self.no_chao = True
                self.pulos_no_ar = 0

    def verificar_colisao_com_plataformas(self, plataformas):
        if self.no_chao or self.velocidade_y < 0:
            return

        for plataforma in plataformas:
            if self.rect.colliderect(plataforma.rect) and self.bottom_anterior <= plataforma.rect.top + 10:
                self.rect.bottom = plataforma.rect.top
                self.pos_y = float(self.rect.y)
                self.velocidade_y = 0
                self.no_chao = True
                self.pulos_no_ar = 0
                break

    def _ferir(self):
        if self.imune > 0:
            return True
        if self.escudo:
            self.escudo = False
            self.imune = FRAMES_IMUNIDADE
            return True
        self.vivo = False
        return False

    def verificar_queda_fatal(self):
        if self.rect.y > self.altura_tela:
            self.vivo = False

    def verificar_colisao_obstaculo(self, lista_de_chaos):
        for chao in lista_de_chaos:
            if chao.obstaculo is not None and self.hitbox.colliderect(chao.obstaculo):
                self._ferir()

    def verificar_colisao_vilao(self, lista_de_chaos):
        for chao in lista_de_chaos:
            if chao.vilao is not None and self.hitbox.colliderect(chao.vilao.hitbox):
                self._ferir()

    def animar(self):
        self.contador_frames += 1

        if self.contador_frames >= self.intervalo_troca:
            self.frame_atual = (self.frame_atual + 1) % len(self.imagens)
            self.contador_frames = 0

    def atualizar(self, lista_de_chaos, plataformas=()):
        if self.imune > 0:
            self.imune -= 1
        self.aplicar_gravidade()
        self.verificar_colisao_com_chao(lista_de_chaos)
        self.verificar_colisao_com_plataformas(plataformas)
        perigos = [*lista_de_chaos, *plataformas]
        self.verificar_colisao_obstaculo(perigos)
        self.verificar_colisao_vilao(perigos)
        self.animar()
        self.verificar_queda_fatal()

    def desenhar(self, tela):
        if self.imune and (self.imune // 4) % 2:
            return
        tela.blit(self.imagens[self.frame_atual], self.rect)
        if self.escudo:
            pygame.draw.circle(tela, cores['azul-jogo'], self.rect.center, max(self.rect.size) // 2 + 8, 4)



