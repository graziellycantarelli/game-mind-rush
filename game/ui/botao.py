import pygame
from game.configuracoes import LARGURA_TELA, ALTURA_TELA


def _carregar(caminho, largura):
    imagem = pygame.image.load(caminho)
    if largura is None:
        return imagem
    altura = round(imagem.get_height() * largura / imagem.get_width())
    return pygame.transform.smoothscale(imagem, (largura, altura))


class Botao:
    def __init__(self, imagem_inicial, centro=(0, 0), imagem_hover=None, largura=None):
        self.imagem = _carregar(imagem_inicial, largura)
        self.imagem_hover = _carregar(imagem_hover, largura) if imagem_hover else self.imagem
        self.rect = self.imagem.get_rect(center=centro)

    def desenhar(self, tela):
        tela.blit(self.obter_imagem_atual(), self.rect)

    def obter_imagem_atual(self):
        return self.imagem_hover if self.esta_em_hover() else self.imagem

    def esta_em_hover(self):
        return self.rect.collidepoint(pygame.mouse.get_pos())

    def clicado(self, pos_clique):
        return self.rect.collidepoint(pos_clique)


def centralizar_em_linha(lista_botoes, y, espaco=40):
    """Fileira horizontal centralizada como grupo, com espaçamento igual entre os botões."""
    largura_total = sum(botao.rect.width for botao in lista_botoes)
    largura_total += espaco * (len(lista_botoes) - 1)

    x_atual = (LARGURA_TELA - largura_total) // 2

    for botao in lista_botoes:
        botao.rect.centerx = x_atual + botao.rect.width // 2
        botao.rect.centery = y
        x_atual += botao.rect.width + espaco


def organizar_em_colunas(colunas, y_base, espaco_x=40, espaco_y=20):
    """Cada coluna é uma lista de botões empilhados; o grupo fica centralizado e termina em y_base."""
    larguras = [max(botao.rect.width for botao in coluna) for coluna in colunas]
    x_atual = (LARGURA_TELA - sum(larguras) - espaco_x * (len(colunas) - 1)) // 2

    for coluna, largura in zip(colunas, larguras):
        y = y_base
        for botao in reversed(coluna):
            botao.rect.bottom = y
            botao.rect.centerx = x_atual + largura // 2
            y = botao.rect.top - espaco_y
        x_atual += largura + espaco_x


def _botao(nome, largura=None):
    return Botao(f"./img/botoes/{nome}MR.png", imagem_hover=f"./img/botoes/{nome}MR_HOVER.png", largura=largura)


LARGURA_BOTAO_MENU = int(LARGURA_TELA * 0.2)
LARGURA_BOTAO_GAMEOVER = int(LARGURA_TELA * 0.28)


# botões do menu
botao_jogar = _botao("JOGAR", LARGURA_BOTAO_MENU)
botao_modos = _botao("MODOS", LARGURA_BOTAO_MENU)
botao_flashcards = _botao("FLASHCARDS", LARGURA_BOTAO_MENU)
botao_loja = _botao("LOJA", LARGURA_BOTAO_MENU)
botao_ranking = _botao("RANKING", LARGURA_BOTAO_MENU)
botao_estatisticas = _botao("ESTATISTICAS", LARGURA_BOTAO_MENU)
botao_config = _botao("CONFIG", LARGURA_BOTAO_MENU)
botao_sair = _botao("SAIR", LARGURA_BOTAO_MENU)

# botões do game over
botao_reiniciar = _botao("REINICIAR", LARGURA_BOTAO_GAMEOVER)
botao_sair_gameover = _botao("SAIRGO", LARGURA_BOTAO_GAMEOVER)
botao_menu = _botao("MENU", LARGURA_BOTAO_GAMEOVER)

organizar_em_colunas(
    [[botao_jogar, botao_modos],
     [botao_flashcards, botao_loja],
     [botao_ranking, botao_estatisticas],
     [botao_config, botao_sair]],
    y_base=int(ALTURA_TELA * 0.97),
    espaco_x=int(LARGURA_TELA * 0.02),
    espaco_y=int(ALTURA_TELA * 0.02)
)

centralizar_em_linha(
    [botao_reiniciar, botao_menu, botao_sair_gameover],
    y=int(ALTURA_TELA * 0.85)
)



