import pygame

from game.configuracoes import LARGURA_TELA, ALTURA_TELA
from game.ui.estilo import COR_TINTA, PALETAS, desenhar_botao_pixel
from game.ui.fontes import FontePixel, esc
from game.ui.icones import desenhar_icone

Y_RESUMO = 0.60   # topo dos quadros, como fração da altura da tela
ESPACO = esc(14)
PREENCHIMENTO = esc(12)
UNIDADE_ICONE = esc(5)
BRANCO = (255, 255, 255)

FONTE_VALOR = FontePixel(48)
FONTE_ROTULO = FontePixel(22)
FONTE_RECORDE = FontePixel(34)

# chave, rótulo, ícone, paleta
CAMPOS = (
    ("pontos", "PONTOS", "estrela", "azul"),
    ("acertos", "ACERTOS", "check", "verde"),
    ("erros", "ERROS", "cruz", "vermelho"),
    ("combo", "COMBO", "chama", "roxo"),
    ("moedas", "MOEDAS", "moeda", "dourado"),
)


def _texto(fonte, texto, cor, sombra):
    frente = fonte.render(texto, True, cor)
    fundo = fonte.render(texto, True, sombra)
    superficie = pygame.Surface((frente.get_width() + esc(3), frente.get_height() + esc(3)), pygame.SRCALPHA)
    superficie.blit(fundo, (esc(3), esc(3)))
    superficie.blit(frente, (0, 0))
    return superficie


class PainelResumo:
    """Quadros com os números da partida, no estilo dos botões do jogo."""

    def __init__(self):
        largura = int(LARGURA_TELA * 0.72)
        largura_cartao = (largura - (len(CAMPOS) - 1) * ESPACO) // len(CAMPOS)
        altura_cartao = (2 * PREENCHIMENTO + 7 * UNIDADE_ICONE + FONTE_VALOR.get_linesize()
                         + FONTE_ROTULO.get_linesize() + 2 * esc(8) + esc(12))
        x = (LARGURA_TELA - largura) // 2
        y = int(ALTURA_TELA * Y_RESUMO)
        self.cartoes = [pygame.Rect(x + i * (largura_cartao + ESPACO), y, largura_cartao, altura_cartao)
                        for i in range(len(CAMPOS))]
        self.centro_recorde = (LARGURA_TELA // 2, y - esc(46))

    def desenhar(self, tela, resumo):
        for rect, (chave, rotulo, icone, nome_paleta) in zip(self.cartoes, CAMPOS):
            paleta = PALETAS[nome_paleta]
            desenhar_botao_pixel(tela, rect, paleta)

            y = rect.y + PREENCHIMENTO + esc(8)
            desenhar_icone(tela, icone, (rect.centerx, y + 7 * UNIDADE_ICONE // 2), UNIDADE_ICONE, BRANCO, paleta[0])
            y += 7 * UNIDADE_ICONE + esc(8)

            valor = f"x{resumo[chave]}" if chave == "combo" else str(resumo[chave])
            numero = _texto(FONTE_VALOR, valor, BRANCO, paleta[0])
            tela.blit(numero, numero.get_rect(midtop=(rect.centerx, y)))
            y += FONTE_VALOR.get_linesize()

            texto = _texto(FONTE_ROTULO, rotulo, paleta[3], paleta[0])
            tela.blit(texto, texto.get_rect(midtop=(rect.centerx, y)))

        if resumo["recorde"]:
            self._desenhar_recorde(tela)

    def _desenhar_recorde(self, tela):
        texto = FONTE_RECORDE.render("NOVO RECORDE!", True, COR_TINTA)
        faixa = pygame.Rect(0, 0, texto.get_width() + 4 * ESPACO, texto.get_height() + 2 * ESPACO)
        pulo = esc(4) if (pygame.time.get_ticks() // 350) % 2 else 0
        faixa.center = (self.centro_recorde[0], self.centro_recorde[1] - pulo)
        desenhar_botao_pixel(tela, faixa, PALETAS["dourado"])
        tela.blit(texto, texto.get_rect(center=(faixa.centerx, faixa.centery - esc(3))))
