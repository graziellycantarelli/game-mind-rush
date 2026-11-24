import os

MODO_PADRAO = "flashcard"
FUNDO_PADRAO = "./img/fundos/bg_jogo.png"
CHAO_PADRAO = "./img/elementos/chao.png"
OBSTACULO_PADRAO = "./img/elementos/obstaculo.png"


def _frames(pasta, nome):
    return [f"./img/{pasta}/{nome}_pos{i}.png" for i in range(3)]


TEMAS = {
    "flashcard": {
        "personagem": _frames("personagens/flashcard", "estudante"),
        "vilao": _frames("viloes/flashcard", "vilao"),
    },
    "computacao": {
        "personagem": _frames("personagens/computacao", "personagem"),
        "vilao": _frames("viloes/computacao", "vilao"),
    },
    "historia": {
        "personagem": _frames("personagens/historia", "personagem"),
        "vilao": _frames("viloes/historia", "vilao"),
    },
    "medvet": {
        "personagem": _frames("personagens/medvet", "personagem"),
        "vilao": _frames("viloes/medvet", "vilao"),
    },
    "letras": {
        "personagem": _frames("personagens/letras", "personagem"),
        "vilao": _frames("viloes/letras", "vilao"),
    },
}

NOMES_MODOS = {
    "flashcard": "Flashcards",
    "computacao": "Computação",
    "historia": "História",
    "medvet": "Medicina Veterinária",
    "letras": "Letras",
}

FUNDOS = {
    "flashcard": FUNDO_PADRAO,
    "computacao": "./img/fundos/bg_computacao.png",
    "historia": "./img/fundos/bg_historia.png",
    "medvet": "./img/fundos/bg_medvet.png",
    "letras": "./img/fundos/bg_letras.png",
}


def tema(modo):
    """Imagens do modo; o que ainda não existe usa as do modo padrão."""
    padrao = TEMAS[MODO_PADRAO]
    return {
        chave: caminhos if all(os.path.exists(c) for c in caminhos) else padrao[chave]
        for chave, caminhos in TEMAS[modo].items()
    }


def _existente(caminho, padrao):
    return caminho if os.path.exists(caminho) else padrao


def caminho_fundo(modo):
    """Fundo do modo; se a imagem ainda não existe, usa o padrão."""
    return _existente(FUNDOS[modo], FUNDO_PADRAO)


def caminho_chao(modo):
    return _existente(f"./img/elementos/chao_{modo}.png", CHAO_PADRAO)


def caminho_obstaculo(modo):
    return _existente(f"./img/elementos/obstaculo_{modo}.png", OBSTACULO_PADRAO)


QUANTIDADE_OBSTACULOS = 5


def caminhos_obstaculos(modo):
    """Os obstáculos do modo que existem; sem nenhum, vale o obstáculo único de antes."""
    caminhos = [f"./img/elementos/obstaculos/{modo}/obstaculo_{i}.png" for i in range(1, QUANTIDADE_OBSTACULOS + 1)]
    return [c for c in caminhos if os.path.exists(c)] or [caminho_obstaculo(modo)]


def caminhos_viloes(modo):
    """Quadros do vilão do modo e, se existir, do segundo vilão."""
    viloes = [tema(modo)["vilao"]]
    segundo = _frames(f"viloes/{modo}", "vilao2")
    if all(os.path.exists(c) for c in segundo):
        viloes.append(segundo)
    return viloes
