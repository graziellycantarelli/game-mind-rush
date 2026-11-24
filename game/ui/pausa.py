import pygame

from game.configuracoes import LARGURA_TELA, ALTURA_TELA
from game.ui.estilo import (COR_DICA, COR_MADEIRA, COR_MADEIRA_ESCURA, COR_TITULO, CORES_ALTERNATIVAS,
                            desenhar_bloco_pixel, escurecer)
from game.ui.fontes import FontePixel, esc, renderizar
from game.util.cores import cores

OPCOES = (("CONTINUAR", "continuar"), ("REINICIAR", "reiniciar"), ("MENU", "menu"))
MARGEM = esc(30)
ESPACO = esc(16)
BRANCO = (255, 255, 255)

FONTE_TITULO = FontePixel(46)
FONTE_BOTAO = FontePixel(34)
FONTE_DICA = FontePixel(22)


class TelaPausa:
    def __init__(self):
        self.escurecer = pygame.Surface((LARGURA_TELA, ALTURA_TELA), pygame.SRCALPHA)
        self.escurecer.fill((0, 0, 0, 170))

        largura_botao, altura_botao = esc(420), esc(76)
        altura = (MARGEM + FONTE_TITULO.get_linesize() + ESPACO + len(OPCOES) * (altura_botao + ESPACO)
                  + FONTE_DICA.get_linesize() + MARGEM)
        self.painel = pygame.Rect(0, 0, largura_botao + 2 * MARGEM, altura)
        self.painel.center = (LARGURA_TELA // 2, ALTURA_TELA // 2)

        y = self.painel.y + MARGEM + FONTE_TITULO.get_linesize() + ESPACO
        self.botoes = [pygame.Rect(self.painel.x + MARGEM, y + i * (altura_botao + ESPACO), largura_botao, altura_botao)
                       for i in range(len(OPCOES))]

    def tratar_evento(self, evento):
        """Devolve "continuar", "reiniciar" ou "menu"."""
        if evento.type == pygame.KEYDOWN and evento.key in (pygame.K_ESCAPE, pygame.K_p):
            return "continuar"
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            for rect, (_, acao) in zip(self.botoes, OPCOES):
                if rect.collidepoint(evento.pos):
                    return acao
        return None

    def desenhar(self, tela):
        tela.blit(self.escurecer, (0, 0))
        desenhar_bloco_pixel(tela, self.painel, COR_MADEIRA, COR_MADEIRA_ESCURA,
                             canto=esc(10), espessura=esc(8), sombra=esc(10))

        titulo = renderizar(FONTE_TITULO, "PAUSA", COR_TITULO)
        tela.blit(titulo, titulo.get_rect(midtop=(self.painel.centerx, self.painel.y + MARGEM)))

        mouse = pygame.mouse.get_pos()
        for rect, (texto, _) in zip(self.botoes, OPCOES):
            cor = cores['verde-logo'] if rect.collidepoint(mouse) else CORES_ALTERNATIVAS[0]
            desenhar_bloco_pixel(tela, rect, cor, escurecer(cor, 0.45), canto=esc(5), espessura=esc(5))
            rotulo = renderizar(FONTE_BOTAO, texto, BRANCO)
            tela.blit(rotulo, rotulo.get_rect(center=rect.center))

        dica = "M: liga e desliga o som"
        tela.blit(renderizar(FONTE_DICA, dica, COR_DICA), (self.painel.x + MARGEM, self.painel.bottom - MARGEM - FONTE_DICA.get_linesize()))

