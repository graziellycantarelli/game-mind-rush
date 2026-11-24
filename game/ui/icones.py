import pygame

ICONES = {
    "estrela": ["...W...", "...W...", "WWWWWWW", ".WWWWW.", "..WWW..", ".WW.WW.", ".W...W."],
    "check": [".......", "......W", ".....WW", "W...WW.", "WW.WW..", ".WWW...", "..W...."],
    "cruz": ["W.....W", "WW...WW", ".WW.WW.", "..WWW..", ".WW.WW.", "WW...WW", "W.....W"],
    "chama": ["...W...", "..WW...", "..WWW..", ".WWWW.W", ".WWWWWW", ".WWWWWW", "..WWWW."],
    "moeda": ["..WWW..", ".W...W.", "W..W..W", "W..W..W", "W..W..W", ".W...W.", "..WWW.."],
    "pausa": [".......", ".WW.WW.", ".WW.WW.", ".WW.WW.", ".WW.WW.", ".WW.WW.", "......."],
    "som": ["...W.....", "..WW...W.", "WWWW.W..W", "WWWW.W..W", "WWWW.W..W", "..WW...W.", "...W....."],
    "seta_esquerda": ["...W...", "..WW...", ".WWWWWW", "WWWWWWW", ".WWWWWW", "..WW...", "...W..."],
    "seta_direita": ["...W...", "...WW..", "WWWWWW.", "WWWWWWW", "WWWWWW.", "...WW..", "...W..."],
    "trofeu": ["WWWWWWWWW", "W.WWWWW.W", "W.WWWWW.W", ".W.WWW.W.", "..WWWWW..", "...WWW...", "....W....",
               "...WWW...", "..WWWWW.."],
    "coroa": ["W...W...W", "WW.WWW.WW", "WWWWWWWWW", "WWWWWWWWW", ".WWWWWWW."],
    "usuario": ["..WWW..", ".WWWWW.", ".WWWWW.", "..WWW..", ".WWWWW.", "WWWWWWW", "WWWWWWW"],
    "email": ["WWWWWWWWW", "WW.....WW", "W.W...W.W", "W..W.W..W", "W...W...W", "W.......W", "WWWWWWWWW"],
    "cadeado": ["..WWW..", ".W...W.", ".W...W.", "WWWWWWW", "WWW.WWW", "WWW.WWW", "WWWWWWW"],
    "calendario": ["W.W.W.W", "WWWWWWW", "W.....W", "W.W.W.W", "W.....W", "W.W.W.W", "WWWWWWW"],
    "musica": ["..WWWWW", "..W...W", "..W...W", "..W...W", ".WW..WW", "WWW.WWW", ".W...W."],
}


def desenhar_icone(tela, nome, centro, unidade, cor=(255, 255, 255), sombra=None):
    mapa = ICONES[nome]
    x0 = centro[0] - len(mapa[0]) * unidade // 2
    y0 = centro[1] - len(mapa) * unidade // 2
    deslocamento = max(1, unidade // 2)
    for cor_atual, desvio in ((sombra, deslocamento), (cor, 0)):
        if cor_atual is None:
            continue
        for linha, texto in enumerate(mapa):
            for coluna, v in enumerate(texto):
                if v == "W":
                    pygame.draw.rect(tela, cor_atual,
                                     (x0 + coluna * unidade + desvio, y0 + linha * unidade + desvio, unidade, unidade))
