import math

import pygame

from game.configuracoes import LARGURA_TELA, ALTURA_TELA
from game.ui.estilo import (COR_DICA, COR_TINTA, COR_TITULO, COR_CERTA, COR_ERRADA, COR_ALERTA,
                            COR_NEUTRA, COR_ERRO_TEXTO, COR_MADEIRA_ESCURA, CORES_ALTERNATIVAS,
                            desenhar_placa, desenhar_papel, desenhar_botao_colorido, clarear)
from game.ui.fontes import FontePixel, arial, esc, renderizar
from game.util.cores import cores

# o texto da pergunta usa Arial inteira: misturar com a fonte pixel dificultava a leitura
FONTE_ENUNCIADO = arial(42)
FONTE_ALTERNATIVA = arial(36)
FONTE_AVISO = arial(32)
FONTE_TITULO = FontePixel(36)

BRANCO = (255, 255, 255)
TECLAS = (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4)
TEMPO_LIMITE = 20   
TEMPO_ESGOTADO = -1

MARGEM = esc(30)
PREENCHIMENTO = esc(14)
ESPACO = esc(12)
FOLGA_LINHA = esc(8)
RAIO_NUMERO = esc(20)
ALTURA_BARRA = esc(12)
RELEVO = esc(5)
RECUO_TEXTO = 2 * PREENCHIMENTO + 2 * RAIO_NUMERO


def quebrar_linhas(texto, fonte, largura):
    linhas, atual = [], ""
    for palavra in texto.split():
        teste = f"{atual} {palavra}".strip()
        if fonte.size(teste)[0] <= largura:
            atual = teste
        else:
            if atual:
                linhas.append(atual)
            atual = palavra
    if atual:
        linhas.append(atual)
    return linhas or [""]


class TelaPergunta:
    def __init__(self):
        self.pergunta = None
        self.escolhida = None
        self.tempo = TEMPO_LIMITE
        self.aberta_em = 0
        self.escurecer = pygame.Surface((LARGURA_TELA, ALTURA_TELA), pygame.SRCALPHA)
        self.escurecer.fill((0, 0, 0, 170))

    def abrir(self, pergunta):
        self.pergunta = pergunta
        self.escolhida = None
        self.tempo = TEMPO_LIMITE
        self.aberta_em = pygame.time.get_ticks()
        self._montar_layout()

    def atualizar(self):
        """Conta o tempo quando acaba, a pergunta vale como errada."""
        if self.escolhida is not None:
            return
        self.tempo = max(0, TEMPO_LIMITE - (pygame.time.get_ticks() - self.aberta_em) / 1000)
        if self.tempo == 0:
            self.escolhida = TEMPO_ESGOTADO

    def _montar_layout(self):
        largura_painel = int(LARGURA_TELA * 0.72)
        largura_texto = largura_painel - 2 * MARGEM
        self.alt_enunciado = FONTE_ENUNCIADO.get_linesize() + FOLGA_LINHA
        self.alt_alternativa = FONTE_ALTERNATIVA.get_linesize() + FOLGA_LINHA

        self.linhas_enunciado = quebrar_linhas(
            self.pergunta["enunciado"], FONTE_ENUNCIADO, largura_texto - 2 * PREENCHIMENTO)

        y = MARGEM + FONTE_TITULO.get_linesize() + ESPACO
        barra = pygame.Rect(MARGEM, y, largura_texto, ALTURA_BARRA)
        y += ALTURA_BARRA + ESPACO
        altura_caixa = len(self.linhas_enunciado) * self.alt_enunciado + 2 * PREENCHIMENTO
        caixa = pygame.Rect(MARGEM, y, largura_texto, altura_caixa)
        y += altura_caixa + 2 * ESPACO

        botoes = []
        for texto in self.pergunta["alternativas"]:
            linhas = quebrar_linhas(texto, FONTE_ALTERNATIVA, largura_texto - RECUO_TEXTO - PREENCHIMENTO)
            altura = max(len(linhas) * self.alt_alternativa, 2 * RAIO_NUMERO) + 2 * PREENCHIMENTO
            botoes.append((pygame.Rect(MARGEM, y, largura_texto, altura), linhas))
            y += altura + ESPACO + RELEVO

        aviso = pygame.Rect(MARGEM, y, largura_texto, FONTE_AVISO.get_linesize() + PREENCHIMENTO)

        self.painel = pygame.Rect(0, 0, largura_painel, aviso.bottom + MARGEM)
        self.painel.center = (LARGURA_TELA // 2, ALTURA_TELA // 2)
        self.pos_titulo = (self.painel.x + MARGEM, self.painel.y + MARGEM)
        self.barra_tempo = barra.move(self.painel.topleft)
        self.caixa_enunciado = caixa.move(self.painel.topleft)
        self.rect_aviso = aviso.move(self.painel.topleft)
        self.botoes = [(rect.move(self.painel.topleft), linhas) for rect, linhas in botoes]

    def tratar_evento(self, evento):
        """Devolve "acertou" ou "errou" depois que o jogador responde e clica para continuar."""
        if self.escolhida is not None:
            continuar = evento.type == pygame.MOUSEBUTTONDOWN or (
                evento.type == pygame.KEYDOWN and evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER))
            if continuar:
                return "acertou" if self.escolhida == self.pergunta["correta"] else "errou"
            return None

        if evento.type == pygame.MOUSEBUTTONDOWN:
            for i, (rect, _) in enumerate(self.botoes):
                if rect.collidepoint(evento.pos):
                    self.escolhida = i
        elif evento.type == pygame.KEYDOWN and evento.key in TECLAS:
            self.escolhida = TECLAS.index(evento.key)
        return None

    def _cor_botao(self, indice, sobre):
        if self.escolhida is None:
            cor = CORES_ALTERNATIVAS[indice % len(CORES_ALTERNATIVAS)]
            return clarear(cor) if sobre else cor
        if indice == self.pergunta["correta"]:
            return COR_CERTA
        return COR_ERRADA if indice == self.escolhida else COR_NEUTRA

    def _aviso(self):
        if self.escolhida is None:
            return "Clique em uma resposta ou aperte 1 a 4", COR_DICA
        if self.escolhida == TEMPO_ESGOTADO:
            return "Tempo esgotado! A certa está em verde. Clique para continuar", COR_ERRO_TEXTO
        if self.escolhida == self.pergunta["correta"]:
            return "Acertou! Clique para continuar", cores['verde-logo']
        return "Errou! A certa está em verde. Clique para continuar", COR_ERRO_TEXTO

    def _desenhar_tempo(self, tela):
        fracao = self.tempo / TEMPO_LIMITE
        cor = cores['verde-logo'] if fracao > 0.5 else COR_ALERTA if fracao > 0.2 else COR_ERRADA
        pygame.draw.rect(tela, COR_MADEIRA_ESCURA, self.barra_tempo, border_radius=6)
        cheia = self.barra_tempo.copy()
        cheia.width = round(self.barra_tempo.width * fracao)
        if cheia.width:
            pygame.draw.rect(tela, cor, cheia, border_radius=6)
        segundos = renderizar(FONTE_TITULO, f"{math.ceil(self.tempo)}s", cor)
        tela.blit(segundos, segundos.get_rect(topright=(self.painel.right - MARGEM, self.pos_titulo[1])))

    def desenhar(self, tela):
        tela.blit(self.escurecer, (0, 0))
        desenhar_placa(tela, self.painel)
        tela.blit(renderizar(FONTE_TITULO, "PERGUNTA", COR_TITULO), self.pos_titulo)
        self._desenhar_tempo(tela)

        desenhar_papel(tela, self.caixa_enunciado)
        y = self.caixa_enunciado.y + PREENCHIMENTO
        for linha in self.linhas_enunciado:
            tela.blit(FONTE_ENUNCIADO.render(linha, True, COR_TINTA), (self.caixa_enunciado.x + PREENCHIMENTO, y))
            y += self.alt_enunciado

        mouse = pygame.mouse.get_pos()
        for i, (rect, linhas) in enumerate(self.botoes):
            cor = self._cor_botao(i, self.escolhida is None and rect.collidepoint(mouse))
            desenhar_botao_colorido(tela, rect, cor, RELEVO)

            centro = (rect.x + PREENCHIMENTO + RAIO_NUMERO, rect.centery)
            pygame.draw.circle(tela, BRANCO, centro, RAIO_NUMERO)
            numero = FONTE_ALTERNATIVA.render(str(i + 1), True, cor)
            tela.blit(numero, numero.get_rect(center=centro))

            y = rect.centery - len(linhas) * self.alt_alternativa // 2
            for linha in linhas:
                tela.blit(renderizar(FONTE_ALTERNATIVA, linha, BRANCO), (rect.x + RECUO_TEXTO, y))
                y += self.alt_alternativa

        pygame.draw.rect(tela, COR_MADEIRA_ESCURA, self.rect_aviso, border_radius=10)
        texto, cor = self._aviso()
        aviso = FONTE_AVISO.render(texto, True, cor)
        tela.blit(aviso, aviso.get_rect(center=self.rect_aviso.center))
