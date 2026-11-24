import pygame
from random import uniform, randint

from game.configuracoes import LARGURA_TELA, ALTURA_TELA

SEQUENCIA = ["sol", "nublado", "chuva", "nublado"]
SEGUNDOS_POR_CLIMA = 20
VELOCIDADE_TRANSICAO = 0.004   # por frame: leva uns 4 segundos para trocar de clima

# nuvens: quantas aparecem | escuro: o quanto a tela escurece | chuva: quantidade de gotas
ESTADOS = {
    "sol":     {"nuvens": 0.3, "escuro": 0.0, "chuva": 0.0},
    "nublado": {"nuvens": 0.8, "escuro": 0.35, "chuva": 0.0},
    "chuva":   {"nuvens": 1.0, "escuro": 0.6, "chuva": 1.0},
}

QUANTIDADE_NUVENS = 7
NUVENS_LEVES = 4        # no mapa dos modos só aparecem poucas nuvens, bem transparentes
OPACIDADE_LEVE = 0.45
QUANTIDADE_GOTAS = 260
ALPHA_ESCURO = 160
COR_ESCURO = (20, 30, 55)
COR_GOTA = (170, 200, 235)

COR_NUVEM = (255, 255, 255)
COR_SOMBRA_NUVEM = (200, 210, 225)
TAMANHO_PIXEL = max(4, LARGURA_TELA // 240)   # tamanho de cada "pixel" da nuvem na tela
FAIXA_Y_NUVEM = (0.0, 0.14)                   # altura em que as nuvens nascem (fração da tela)
FORMA_NUVEM = ((0.22, 0.65, 0.17), (0.42, 0.50, 0.22), (0.65, 0.55, 0.20),
                (0.82, 0.70, 0.14), (0.50, 0.70, 0.15))


class Nuvem:
    def __init__(self):
        largura = int(LARGURA_TELA * uniform(0.12, 0.24)) // TAMANHO_PIXEL
        self.imagem = self._desenhar(largura)
        self.velocidade = uniform(0.5, 1.3)
        self.x = uniform(-self.imagem.get_width(), LARGURA_TELA)
        self.y = ALTURA_TELA * uniform(*FAIXA_Y_NUVEM)

    @staticmethod
    def _desenhar(largura):
        altura = largura // 2
        imagem = pygame.Surface((largura, altura), pygame.SRCALPHA)

        # a sombra vem primeiro, um pixel mais baixa; o branco cobre quase tudo por cima
        for cor, descida in ((COR_SOMBRA_NUVEM, 1), (COR_NUVEM, 0)):
            for x, y, raio in FORMA_NUVEM:
                centro = (int(x * largura), int(y * altura) + descida)
                pygame.draw.circle(imagem, cor, centro, int(raio * largura))

        # desenhada pequena e ampliada sem suavizar, o que dá o efeito pixelado
        tamanho = (largura * TAMANHO_PIXEL, altura * TAMANHO_PIXEL)
        return pygame.transform.scale(imagem, tamanho)

    def mover(self):
        self.x -= self.velocidade
        if self.x + self.imagem.get_width() < 0:
            self.x = LARGURA_TELA
            self.y = ALTURA_TELA * uniform(*FAIXA_Y_NUVEM)

    def desenhar(self, tela, opacidade):
        self.imagem.set_alpha(int(255 * opacidade))
        tela.blit(self.imagem, (int(self.x), int(self.y)))


class Gota:
    def __init__(self):
        self.reiniciar()
        self.y = uniform(0, ALTURA_TELA)

    def reiniciar(self):
        self.comprimento = randint(14, 24)
        self.velocidade = randint(14, 22)
        self.x = uniform(0, LARGURA_TELA + 250)
        self.y = -self.comprimento

    def mover(self):
        self.y += self.velocidade
        self.x -= self.velocidade * 0.2
        if self.y > ALTURA_TELA:
            self.reiniciar()

    def desenhar(self, tela):
        inicio = (self.x, self.y)
        fim = (self.x + self.comprimento * 0.2, self.y - self.comprimento)
        pygame.draw.line(tela, COR_GOTA, inicio, fim, 2)


class Clima:
    def __init__(self):
        self.indice = 0
        self.inicio = pygame.time.get_ticks()
        self.valores = dict(ESTADOS[SEQUENCIA[0]])

        self.nuvens = [Nuvem() for _ in range(QUANTIDADE_NUVENS)]
        self.gotas = [Gota() for _ in range(QUANTIDADE_GOTAS)]

        self.escurecer = pygame.Surface((LARGURA_TELA, ALTURA_TELA))
        self.escurecer.fill(COR_ESCURO)

    @property
    def nome(self):
        return SEQUENCIA[self.indice]

    def atualizar(self):
        agora = pygame.time.get_ticks()
        if agora - self.inicio >= SEGUNDOS_POR_CLIMA * 1000:
            self.indice = (self.indice + 1) % len(SEQUENCIA)
            self.inicio = agora

        # cada valor anda um pouquinho por frame em direção ao do clima atual
        for chave, alvo in ESTADOS[self.nome].items():
            passo = max(-VELOCIDADE_TRANSICAO, min(VELOCIDADE_TRANSICAO, alvo - self.valores[chave]))
            self.valores[chave] += passo

        for nuvem in self.nuvens:
            nuvem.mover()

        if self.valores["chuva"] > 0:
            for gota in self.gotas:
                gota.mover()

    def desenhar(self, tela, leve=False):
        if leve:
            for nuvem in self.nuvens[:NUVENS_LEVES]:
                nuvem.desenhar(tela, OPACIDADE_LEVE)
            return

        nuvens_visiveis = self.valores["nuvens"] * len(self.nuvens)
        for i, nuvem in enumerate(self.nuvens):
            opacidade = max(0, min(1, nuvens_visiveis - i))
            if opacidade > 0:
                nuvem.desenhar(tela, opacidade)

        if self.valores["escuro"] > 0:
            self.escurecer.set_alpha(int(ALPHA_ESCURO * self.valores["escuro"]))
            tela.blit(self.escurecer, (0, 0))

        quantidade = int(len(self.gotas) * self.valores["chuva"])
        for gota in self.gotas[:quantidade]:
            gota.desenhar(tela)
