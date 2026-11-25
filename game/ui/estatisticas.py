import pygame

from game.configuracoes import LARGURA_TELA, ALTURA_TELA, imagem_bg_cadastro
from game.database import estatisticas_db
from game.temas import NOMES_MODOS
from game.ui.conta import BotaoTexto, COR_BOTAO_NEUTRO, FONTE_TITULO_TELA, desenhar_fundo
from game.ui.estilo import (COR_CREME, COR_TINTA, COR_TITULO, COR_CERTA, COR_ERRADA, COR_MADEIRA_ESCURA,
                            CORES_ALTERNATIVAS, desenhar_placa, desenhar_papel)
from game.ui.fontes import FontePixel, arial, esc, renderizar

MARGEM = esc(30)
PREENCHIMENTO = esc(14)
ESPACO = esc(12)
QUANTIDADE_CARTOES = 4
COR_OURO = (190, 130, 20)
# melhor pontuação, partidas, moedas e perguntas para revisar
CORES_VALORES = (CORES_ALTERNATIVAS[2], CORES_ALTERNATIVAS[0], COR_OURO, CORES_ALTERNATIVAS[3])

FONTE_VALOR = FontePixel(56)
FONTE_ROTULO = arial(28)
FONTE_SECAO = arial(30)
FONTE_LINHA = arial(32)
ALTURA_BARRA = FONTE_LINHA.get_linesize() // 2
LARGURA_NOME = FONTE_LINHA.size("Medicina Veterinária")[0] + ESPACO
LARGURA_PLACAR = FONTE_LINHA.size("9999 acertos, 9999 erros")[0]


class TelaEstatisticas:
    def __init__(self):
        self.valores = []
        self.materias = {}

        largura = int(LARGURA_TELA * 0.7)
        self.altura_linha = FONTE_LINHA.get_linesize() + ESPACO
        altura_cartao = FONTE_VALOR.get_linesize() + FONTE_ROTULO.get_linesize() + 2 * PREENCHIMENTO
        altura = (2 * MARGEM + altura_cartao + 2 * ESPACO + FONTE_SECAO.get_linesize() + ESPACO
                  + len(NOMES_MODOS) * self.altura_linha)

        self.painel = pygame.Rect(0, 0, largura, altura)
        self.painel.center = (LARGURA_TELA // 2, ALTURA_TELA // 2)

        x = self.painel.x + MARGEM
        largura_cartao = (largura - 2 * MARGEM - (QUANTIDADE_CARTOES - 1) * ESPACO) // QUANTIDADE_CARTOES
        self.cartoes = [
            pygame.Rect(x + i * (largura_cartao + ESPACO), self.painel.y + MARGEM, largura_cartao, altura_cartao)
            for i in range(QUANTIDADE_CARTOES)
        ]

        y = self.painel.y + MARGEM + altura_cartao + 2 * ESPACO
        self.pos_secao = (x, y)
        self.y_linhas = y + FONTE_SECAO.get_linesize() + ESPACO
        self.x_barra = x + LARGURA_NOME
        self.largura_barra = largura - 2 * MARGEM - LARGURA_NOME - LARGURA_PLACAR - ESPACO

        self.botao_voltar = BotaoTexto("Voltar", (LARGURA_TELA // 2, self.painel.bottom + 4 * MARGEM),
                                    cor=COR_BOTAO_NEUTRO)

    def abrir(self, jogador):
        dados = estatisticas_db.resumo(jogador["id"])
        self.materias = dados["materias"]
        self.valores = [
            ("Melhor pontuação", dados["melhor"]),
            ("Partidas jogadas", dados["partidas"]),
            ("Moedas ganhas", dados["moedas"]),
            ("Para revisar", dados["revisar"]),
        ]

    def tratar_evento(self, evento):
        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
            return "voltar"
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if self.botao_voltar.clicado(evento.pos):
                return "voltar"
        return None

    def _desenhar_cartoes(self, tela):
        for rect, cor, (rotulo, valor) in zip(self.cartoes, CORES_VALORES, self.valores):
            desenhar_papel(tela, rect, cor)
            numero = FONTE_VALOR.render(str(valor), True, cor)
            tela.blit(numero, numero.get_rect(midtop=(rect.centerx, rect.y + PREENCHIMENTO)))
            texto = FONTE_ROTULO.render(rotulo, True, COR_TINTA)
            tela.blit(texto, texto.get_rect(midbottom=(rect.centerx, rect.bottom - PREENCHIMENTO)))

    def _desenhar_materias(self, tela):
        tela.blit(renderizar(FONTE_SECAO, "Acertos e erros por matéria", COR_TITULO), self.pos_secao)

        for i, (modo, nome) in enumerate(NOMES_MODOS.items()):
            acertos, erros = self.materias.get(modo, (0, 0))
            total = acertos + erros
            y = self.y_linhas + i * self.altura_linha

            tela.blit(renderizar(FONTE_LINHA, nome, COR_CREME), (self.pos_secao[0], y))

            barra = pygame.Rect(self.x_barra, y + (self.altura_linha - ESPACO - ALTURA_BARRA) // 2,
                                self.largura_barra, ALTURA_BARRA)
            pygame.draw.rect(tela, COR_ERRADA if total else COR_MADEIRA_ESCURA, barra, border_radius=8)
            if acertos:
                certa = barra.copy()
                certa.width = round(barra.width * acertos / total)
                pygame.draw.rect(tela, COR_CERTA, certa, border_radius=8)

            placar = f"{acertos} acertos, {erros} erros" if total else "sem respostas"
            texto = renderizar(FONTE_LINHA, placar, COR_CREME)
            tela.blit(texto, texto.get_rect(topright=(self.painel.right - MARGEM, y)))

    def desenhar(self, tela, clima=None):
        desenhar_fundo(tela, imagem_bg_cadastro, clima)
        titulo = renderizar(FONTE_TITULO_TELA, "Estatísticas", COR_TITULO)
        tela.blit(titulo, titulo.get_rect(midbottom=(LARGURA_TELA // 2, self.painel.top - 2 * ESPACO)))

        desenhar_placa(tela, self.painel)
        self._desenhar_cartoes(tela)
        self._desenhar_materias(tela)
        self.botao_voltar.desenhar(tela)

