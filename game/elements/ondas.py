import math
from random import Random

import pygame

COR_AGUA = (18, 130, 215)
TOLERANCIA = (30, 60, 60, 255)
CORES = ((150, 210, 255), (205, 235, 255))
QUANTIDADE = 180


class Ondas:
    """Marquinhas claras que balançam só sobre a água do mapa."""

    def __init__(self, mapa, escala):
        agua = pygame.mask.from_threshold(mapa, COR_AGUA, TOLERANCIA)
        sorteio = Random(7)
        largura, altura = mapa.get_size()
        amplitude = int(14 * escala)
        espessura = max(2, int(4 * escala))

        self.marcas = []
        tentativas = 0
        while len(self.marcas) < QUANTIDADE and tentativas < QUANTIDADE * 30:
            tentativas += 1
            comprimento = int(sorteio.uniform(24, 56) * escala)
            x = sorteio.randrange(amplitude, largura - comprimento - amplitude - 1)
            y = sorteio.randrange(0, altura - espessura - 1)
            if self._so_agua(agua, x - amplitude, x + comprimento + amplitude, y, espessura):
                self.marcas.append({
                    "x": x, "y": y, "comprimento": comprimento, "espessura": espessura,
                    "amplitude": amplitude, "fase": sorteio.uniform(0, 2 * math.pi),
                    "velocidade": sorteio.uniform(1.2, 2.4),
                })

    @staticmethod
    def _so_agua(agua, x1, x2, y, espessura):
        return all(agua.get_at((x, linha)) for x in range(x1, x2 + 1, 6) for linha in (y, y + espessura))

    def desenhar(self, tela, origem):
        tempo = pygame.time.get_ticks() / 1000
        for marca in self.marcas:
            fase = tempo * marca["velocidade"] + marca["fase"]
            comprimento = round(marca["comprimento"] * (0.65 + 0.35 * abs(math.cos(fase))))
            x = origem[0] + marca["x"] + math.sin(fase) * marca["amplitude"]
            tela.fill(CORES[int(fase / math.pi) % 2], (x, origem[1] + marca["y"], comprimento, marca["espessura"]))
