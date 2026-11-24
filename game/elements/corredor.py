import math
from random import randint

from game.configuracoes import ALTURA_TELA

VELOCIDADE = 5
GRAVIDADE = 1
FORCA_SALTO = -20
INTERVALO_TROCA = 6
FOLGA_PULO = 260

# plataformas de pedra atrás dos botões: (x inicial, y dos pés), em fração da tela
PLATAFORMAS = (
    (0.0, 0.648),
    (0.145, 0.621),
    (0.279, 0.609),
    (0.718, 0.621),
    (0.851, 0.648),
)


def _deslocamento(forca, frames):
    return forca * frames + GRAVIDADE * frames * (frames + 1) / 2


class Corredor:
    """Personagem que corre sozinho, só de enfeite, pulando de plataforma em plataforma."""

    def __init__(self, personagem, largura_tela):
        self.personagem = personagem
        self.largura_tela = largura_tela
        self.bordas = [(x * largura_tela, y * ALTURA_TELA) for x, y in PLATAFORMAS]
        self.x = -personagem.largura
        self.y = self.bordas[0][1]
        self.velocidade_y = 0
        self.frame = 0
        self.contador = 0
        self.frames_ate_pular = randint(60, 150)
        self.proximo_pulo = 0
        self._calcular_pulos()

    def _calcular_pulos(self):
        """Para cada plataforma mais alta que a anterior: onde começar o pulo e com que força."""
        folga = 0.02 * ALTURA_TELA
        self.pulos = []
        for (_, y_antes), (x, y) in zip(self.bordas, self.bordas[1:]):
            subida = y_antes - y
            if subida <= 0:
                continue
            forca = -math.sqrt(2 * GRAVIDADE * (subida + folga))
            frames = 1
            while _deslocamento(forca, frames) > -subida:
                frames += 1
            # começa um quadro antes, para já estar acima da borda quando chegar nela
            self.pulos.append((x, forca, VELOCIDADE * (frames + 1)))

    def _chao_em(self, x):
        for x_borda, y in reversed(self.bordas):
            if x >= x_borda:
                return y
        return self.bordas[0][1]

    def _pode_pular_solto(self, x_pe):
        if self.proximo_pulo >= len(self.pulos):
            return True
        return x_pe < self.pulos[self.proximo_pulo][0] - FOLGA_PULO

    def atualizar(self):
        self.x += VELOCIDADE
        if self.x > self.largura_tela:
            self.x = -self.personagem.largura
            self.y = self.bordas[0][1]
            self.velocidade_y = 0
            self.proximo_pulo = 0

        x_pe = self.x + self.personagem.largura / 2
        no_chao = self.y >= self._chao_em(x_pe)

        if self.proximo_pulo < len(self.pulos):
            borda, forca, antecipacao = self.pulos[self.proximo_pulo]
            if x_pe >= borda - antecipacao and no_chao:
                self.velocidade_y = forca
                self.proximo_pulo += 1
            elif x_pe >= borda:
                self.proximo_pulo += 1

        self.frames_ate_pular -= 1
        if self.frames_ate_pular <= 0 and no_chao and self._pode_pular_solto(x_pe):
            self.velocidade_y = FORCA_SALTO
            self.frames_ate_pular = randint(70, 180)

        self.velocidade_y += GRAVIDADE
        self.y += self.velocidade_y
        chao = self._chao_em(x_pe)
        if self.y >= chao:
            self.y = chao
            self.velocidade_y = 0

        self.contador += 1
        if self.contador >= INTERVALO_TROCA:
            self.frame = (self.frame + 1) % len(self.personagem.imagens)
            self.contador = 0

    def desenhar(self, tela):
        imagem = self.personagem.imagens[self.frame % len(self.personagem.imagens)]
        tela.blit(imagem, imagem.get_rect(midbottom=(self.x + imagem.get_width() // 2, self.y)))
