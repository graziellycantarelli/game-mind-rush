import pygame

from game.configuracoes import LARGURA_TELA, ALTURA_TELA
from game.elements.vidas import Vidas
from game.ui.estilo import COR_CREME, COR_DICA, COR_TITULO, CORES_ALTERNATIVAS, desenhar_placa
from game.ui.fontes import renderizar
from game.ui.pergunta import (FONTE_ALTERNATIVA, FONTE_AVISO, FONTE_TITULO, BRANCO, MARGEM, PREENCHIMENTO,
                            ESPACO, FOLGA_LINHA, RAIO_NUMERO, TEMPO_LIMITE, quebrar_linhas)

PASSOS = (
    "Aperte ESPAÇO ou a seta para cima para pular obstáculos, vilões e buracos.",
    f"Pegue as moedas pelo caminho. Cada cérebro traz uma pergunta, e você tem {TEMPO_LIMITE} segundos para responder.",
    f"Resposta errada ou tempo esgotado tira um coração. A cada {Vidas.ACERTOS_PARA_CURAR} acertos você recupera um.",
    "Acertos seguidos aumentam o combo e, a cada 3, você escolhe um power-up.",
    "Use as moedas na loja, dentro de Conta, para comprar skins de personagem com cenário.",
)
ATRASO_ENTRADA_MS = 300


class TelaTutorial:
    def __init__(self):
        self.aberta_em = 0
        self.escurecer = pygame.Surface((LARGURA_TELA, ALTURA_TELA), pygame.SRCALPHA)
        self.escurecer.fill((0, 0, 0, 170))
        self._montar_layout()

    def _montar_layout(self):
        largura_painel = int(LARGURA_TELA * 0.72)
        recuo = 2 * RAIO_NUMERO + PREENCHIMENTO
        self.alt_linha = FONTE_ALTERNATIVA.get_linesize() + FOLGA_LINHA

        y = MARGEM + FONTE_TITULO.get_linesize() + 2 * ESPACO
        passos = []
        for texto in PASSOS:
            linhas = quebrar_linhas(texto, FONTE_ALTERNATIVA, largura_painel - 2 * MARGEM - recuo)
            altura = max(len(linhas) * self.alt_linha, 2 * RAIO_NUMERO)
            passos.append((y, altura, linhas))
            y += altura + 2 * ESPACO

        self.recuo = recuo
        self.painel = pygame.Rect(0, 0, largura_painel, y + FONTE_AVISO.get_linesize() + MARGEM)
        self.painel.center = (LARGURA_TELA // 2, ALTURA_TELA // 2)
        self.passos = passos

    def abrir(self):
        self.aberta_em = pygame.time.get_ticks()

    def tratar_evento(self, evento):
        if pygame.time.get_ticks() - self.aberta_em < ATRASO_ENTRADA_MS:
            return False
        return evento.type in (pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN)

    def desenhar(self, tela):
        tela.blit(self.escurecer, (0, 0))
        desenhar_placa(tela, self.painel)
        tela.blit(renderizar(FONTE_TITULO, "COMO JOGAR", COR_TITULO), (self.painel.x + MARGEM, self.painel.y + MARGEM))

        for i, (y, altura, linhas) in enumerate(self.passos):
            centro = (self.painel.x + MARGEM + RAIO_NUMERO, self.painel.y + y + altura // 2)
            cor = CORES_ALTERNATIVAS[i % len(CORES_ALTERNATIVAS)]
            pygame.draw.circle(tela, cor, centro, RAIO_NUMERO)
            numero = FONTE_ALTERNATIVA.render(str(i + 1), True, BRANCO)
            tela.blit(numero, numero.get_rect(center=centro))

            y_texto = self.painel.y + y + (altura - len(linhas) * self.alt_linha) // 2
            for linha in linhas:
                tela.blit(FONTE_ALTERNATIVA.render(linha, True, COR_CREME),
                        (self.painel.x + MARGEM + self.recuo, y_texto))
                y_texto += self.alt_linha

        aviso = FONTE_AVISO.render("Clique ou aperte qualquer tecla para começar", True, COR_DICA)
        tela.blit(aviso, aviso.get_rect(midbottom=(self.painel.centerx, self.painel.bottom - MARGEM // 2)))
