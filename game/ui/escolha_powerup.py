import pygame

from game.configuracoes import LARGURA_TELA, ALTURA_TELA
from game.elements.powerups import POWERUPS, ACERTOS_PARA_POWERUP
from game.ui.estilo import (COR_CREME, COR_DICA, COR_TITULO, CORES_ALTERNATIVAS, desenhar_placa,
                            desenhar_botao_colorido, clarear)
from game.ui.fontes import renderizar
from game.ui.pergunta import (FONTE_ALTERNATIVA, FONTE_AVISO, FONTE_TITULO, BRANCO, MARGEM, PREENCHIMENTO,
                            ESPACO, RAIO_NUMERO, quebrar_linhas)

TECLAS = [pygame.K_1 + i for i in range(len(POWERUPS))]
ATRASO_ENTRADA_MS = 300   


class TelaPowerUp:
    def __init__(self):
        self.chaves = list(POWERUPS)
        self.aberta_em = 0
        self.escurecer = pygame.Surface((LARGURA_TELA, ALTURA_TELA), pygame.SRCALPHA)
        self.escurecer.fill((0, 0, 0, 170))
        self._montar_layout()

    def _montar_layout(self):
        quantidade = len(self.chaves)
        largura_painel = int(LARGURA_TELA * 0.72)
        largura_carta = (largura_painel - 2 * MARGEM - (quantidade - 1) * ESPACO) // quantidade
        self.alt_nome = FONTE_ALTERNATIVA.get_linesize()
        self.alt_descricao = FONTE_AVISO.get_linesize()

        self.descricoes = {
            chave: quebrar_linhas(POWERUPS[chave]["descricao"], FONTE_AVISO, largura_carta - 2 * PREENCHIMENTO)
            for chave in self.chaves
        }
        linhas_maximo = max(len(linhas) for linhas in self.descricoes.values())
        altura_carta = (PREENCHIMENTO + 2 * RAIO_NUMERO + ESPACO + self.alt_nome + ESPACO
                        + linhas_maximo * self.alt_descricao + PREENCHIMENTO)

        y = MARGEM + FONTE_TITULO.get_linesize() + ESPACO
        self.y_subtitulo = y
        y += self.alt_nome + 2 * ESPACO
        y_cartas = y

        self.painel = pygame.Rect(0, 0, largura_painel,
                                y_cartas + altura_carta + ESPACO + FONTE_AVISO.get_linesize() + MARGEM)
        self.painel.center = (LARGURA_TELA // 2, ALTURA_TELA // 2)
        self.cartas = [
            (chave, pygame.Rect(self.painel.x + MARGEM + i * (largura_carta + ESPACO),
                                self.painel.y + y_cartas, largura_carta, altura_carta))
            for i, chave in enumerate(self.chaves)
        ]

    def abrir(self):
        self.aberta_em = pygame.time.get_ticks()

    def tratar_evento(self, evento):
        """Devolve a chave do power-up escolhido ou None."""
        if pygame.time.get_ticks() - self.aberta_em < ATRASO_ENTRADA_MS:
            return None
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            for chave, rect in self.cartas:
                if rect.collidepoint(evento.pos):
                    return chave
        elif evento.type == pygame.KEYDOWN and evento.key in TECLAS:
            return self.chaves[TECLAS.index(evento.key)]
        return None

    def desenhar(self, tela):
        tela.blit(self.escurecer, (0, 0))
        desenhar_placa(tela, self.painel)

        tela.blit(renderizar(FONTE_TITULO, "POWER-UP", COR_TITULO), (self.painel.x + MARGEM, self.painel.y + MARGEM))
        subtitulo = FONTE_ALTERNATIVA.render(
            f"{ACERTOS_PARA_POWERUP} acertos seguidos! Escolha um:", True, COR_CREME)
        tela.blit(subtitulo, (self.painel.x + MARGEM, self.painel.y + self.y_subtitulo))

        mouse = pygame.mouse.get_pos()
        for i, (chave, rect) in enumerate(self.cartas):
            cor = CORES_ALTERNATIVAS[i % len(CORES_ALTERNATIVAS)]
            desenhar_botao_colorido(tela, rect, clarear(cor) if rect.collidepoint(mouse) else cor)

            centro = (rect.centerx, rect.y + PREENCHIMENTO + RAIO_NUMERO)
            pygame.draw.circle(tela, BRANCO, centro, RAIO_NUMERO)
            numero = FONTE_ALTERNATIVA.render(str(i + 1), True, cor)
            tela.blit(numero, numero.get_rect(center=centro))

            y = centro[1] + RAIO_NUMERO + ESPACO
            nome = FONTE_ALTERNATIVA.render(POWERUPS[chave]["nome"], True, BRANCO)
            tela.blit(nome, nome.get_rect(midtop=(rect.centerx, y)))

            y += self.alt_nome + ESPACO
            for linha in self.descricoes[chave]:
                texto = FONTE_AVISO.render(linha, True, BRANCO)
                tela.blit(texto, texto.get_rect(midtop=(rect.centerx, y)))
                y += self.alt_descricao

        aviso = FONTE_AVISO.render("Clique em um power-up ou aperte 1 a 3", True, COR_DICA)
        tela.blit(aviso, aviso.get_rect(midbottom=(self.painel.centerx, self.painel.bottom - MARGEM // 2)))

