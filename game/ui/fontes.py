import pygame

from game.configuracoes import ALTURA_TELA
from game.util.cores import cores

CAMINHO_FONTE = './fontes/aseprite.ttf'
FONTE_TEM_ACENTOS = False   
ESCALA = ALTURA_TELA / 1080


def esc(valor):
    return max(1, int(valor * ESCALA))


SOMBRA = max(2, esc(3))


def arial(tamanho):
    return pygame.font.SysFont('arial', esc(tamanho), bold=True)


class FontePixel:

    def __init__(self, tamanho):
        self.principal = pygame.font.Font(CAMINHO_FONTE, esc(tamanho))
        self.apoio = pygame.font.SysFont('arial', esc(tamanho), bold=True)
        self.subida = max(self.principal.get_ascent(), self.apoio.get_ascent())
        self.descida = max(-self.principal.get_descent(), -self.apoio.get_descent())

    def _fonte_de(self, char):
        if ord(char) > 127 and not FONTE_TEM_ACENTOS:
            return self.apoio
        return self.principal

    def size(self, texto):
        largura = sum(self._fonte_de(c).size(c)[0] for c in texto)
        return largura, self.subida + self.descida

    def get_linesize(self):
        return self.subida + self.descida

    def render(self, texto, antialias, cor):
        superficie = pygame.Surface(self.size(texto), pygame.SRCALPHA)
        x = 0
        for char in texto:
            fonte = self._fonte_de(char)
            glifo = fonte.render(char, antialias, cor)
            superficie.blit(glifo, (x, self.subida - fonte.get_ascent()))
            x += glifo.get_width()
        return superficie


def renderizar(fonte, texto, cor, cor_sombra=None):
    frente = fonte.render(texto, True, cor)
    sombra = fonte.render(texto, True, cor_sombra or cores['preto'])

    resultado = pygame.Surface((frente.get_width() + SOMBRA, frente.get_height() + SOMBRA), pygame.SRCALPHA)
    resultado.blit(sombra, (SOMBRA, SOMBRA))
    resultado.blit(frente, (0, 0))
    return resultado
