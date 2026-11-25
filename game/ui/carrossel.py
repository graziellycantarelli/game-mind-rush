ESPACO_VIZINHO = 0.92
ESPACO_SEGUINTE = 0.75
SUAVIDADE = 0.18


def lugar(distancia, largura_cartao):
    """Escala e deslocamento horizontal de um cartão."""
    a = abs(distancia)
    escala = 1 - 0.24 * min(a, 1) - 0.10 * max(0, min(a - 1, 1))
    afastamento = a * ESPACO_VIZINHO if a <= 1 else ESPACO_VIZINHO + (a - 1) * ESPACO_SEGUINTE
    return escala, (afastamento * largura_cartao) * (1 if distancia >= 0 else -1)


def suavizar(posicao, indice):
    """Aproxima a posição animada do índice escolhido."""
    diferenca = indice - posicao
    return indice if abs(diferenca) < 0.002 else posicao + diferenca * SUAVIDADE
