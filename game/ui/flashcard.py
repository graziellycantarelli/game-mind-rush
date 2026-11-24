import pygame

from game.configuracoes import LARGURA_TELA, ALTURA_TELA, imagem_bg_cadastro
from game.database import flashcards_db as banco
from game.ui.conta import ALTURA_CAMPO, COR_BOTAO_NEUTRO, CampoTexto, desenhar_fundo
from game.ui.estilo import (COR_CERTA, COR_CREME, COR_DICA, COR_ERRADA, COR_ERRO_TEXTO, COR_MADEIRA_ESCURA,
                            COR_NEUTRA, COR_PAPEL, COR_SUCESSO_TEXTO, COR_TINTA, COR_TITULO, CORES_ALTERNATIVAS,
                            clarear, desenhar_bloco_pixel, desenhar_botao_colorido, desenhar_papel,
                            desenhar_placa, escurecer)
from game.ui.fontes import FontePixel, esc, renderizar
from game.ui.pergunta import quebrar_linhas
from game.util.texto import respostas_iguais

BRANCO = (255, 255, 255)
MARGEM = 30
PREENCHIMENTO = 12
ESPACO = 15
LIMITE_PERGUNTA = 160
LIMITE_RESPOSTA = 100
MINIMO_PARA_JOGAR = 1
ATRASO_ENTRADA_MS = 300   # evita responder sem querer ao abrir
ESPACO_ROTULO = esc(40)
FAIXA_ITEM = 10


def _cortar(texto, fonte, largura):
    if fonte.size(texto)[0] <= largura:
        return texto
    while texto and fonte.size(texto + "...")[0] > largura:
        texto = texto[:-1]
    return texto + "..."


def _desenhar_botao(tela, fonte, rect, texto, cor):
    if rect.collidepoint(pygame.mouse.get_pos()):
        cor = clarear(cor)
    desenhar_bloco_pixel(tela, rect, cor, escurecer(cor, 0.5), canto=esc(4), espessura=esc(4), sombra=esc(4))
    imagem = renderizar(fonte, texto, BRANCO)
    tela.blit(imagem, imagem.get_rect(center=rect.center))


class CampoLinhas:
    def __init__(self, rect, limite, linhas_visiveis):
        self.rect = rect
        self.limite = limite
        self.linhas_visiveis = linhas_visiveis
        self.texto = ""

    def digitar(self, caractere):
        if caractere and caractere.isprintable() and len(self.texto) < self.limite:
            self.texto += caractere

    def apagar(self):
        self.texto = self.texto[:-1]

    def limpar(self):
        self.texto = ""

    def desenhar(self, tela, fonte, focado):
        desenhar_bloco_pixel(tela, self.rect, COR_PAPEL, CORES_ALTERNATIVAS[0] if focado else COR_MADEIRA_ESCURA,
                             canto=esc(4), espessura=esc(4), sombra=0)

        cursor = "|" if focado and (pygame.time.get_ticks() // 500) % 2 == 0 else ""
        largura = self.rect.width - 2 * PREENCHIMENTO
        linhas = quebrar_linhas(self.texto + cursor, fonte, largura)[-self.linhas_visiveis:]

        altura_linha = fonte.get_linesize()
        tela.set_clip(self.rect)
        for n, linha in enumerate(linhas):
            posicao = (self.rect.x + PREENCHIMENTO, self.rect.y + PREENCHIMENTO + n * altura_linha)
            tela.blit(fonte.render(linha, True, COR_TINTA), posicao)
        tela.set_clip(None)


class TelaFlashcards:
    def __init__(self):
        self.fonte = FontePixel(34)
        self.fonte_titulo = FontePixel(46)
        self.jogador_id = None
        self.cartas = []
        self.selecionada = None
        self.rolagem = 0
        self.focado = 0
        self.mensagem = ""
        self.mensagem_ok = False
        self._montar_layout()

    def _montar_layout(self):
        altura_linha = self.fonte.get_linesize()
        largura_painel = int(LARGURA_TELA * 0.9)
        altura_painel = int(ALTURA_TELA * 0.96)
        self.painel = pygame.Rect((LARGURA_TELA - largura_painel) // 2,
                                  (ALTURA_TELA - altura_painel) // 2,
                                  largura_painel, altura_painel)

        x0 = self.painel.x + MARGEM
        y_conteudo = self.painel.y + MARGEM + self.fonte_titulo.get_linesize() + ESPACO
        self.pos_titulo = (x0, self.painel.y + MARGEM)

        largura_lista = int(largura_painel * 0.42)
        self.pos_cabecalho_lista = (x0, y_conteudo)
        self.alt_item = altura_linha + 14
        y_lista = y_conteudo + altura_linha + 8
        self.lista = pygame.Rect(x0, y_lista, largura_lista, self.painel.bottom - MARGEM - y_lista)
        self.visiveis = max(1, self.lista.height // self.alt_item)

        x_dir = self.lista.right + MARGEM
        largura_dir = self.painel.right - MARGEM - x_dir
        y = y_conteudo
        self.pos_rotulo_pergunta = (x_dir, y)
        y += altura_linha + 4
        self.campo_pergunta = CampoLinhas(
            pygame.Rect(x_dir, y, largura_dir, 3 * altura_linha + 2 * PREENCHIMENTO),
            LIMITE_PERGUNTA, 3)
        y = self.campo_pergunta.rect.bottom + ESPACO
        self.pos_rotulo_resposta = (x_dir, y)
        y += altura_linha + 4
        self.campo_resposta = CampoLinhas(
            pygame.Rect(x_dir, y, largura_dir, 2 * altura_linha + 2 * PREENCHIMENTO),
            LIMITE_RESPOSTA, 2)
        y = self.campo_resposta.rect.bottom + ESPACO
        self.pos_mensagem = (x_dir, y)
        y += altura_linha + ESPACO

        altura_botao = altura_linha + 2 * PREENCHIMENTO
        largura_botao = (largura_dir - ESPACO) // 2
        self.botao_adicionar = pygame.Rect(x_dir, y, largura_botao, altura_botao)
        self.botao_apagar = pygame.Rect(x_dir + largura_botao + ESPACO, y, largura_botao, altura_botao)
        y += altura_botao + ESPACO
        self.botao_jogar = pygame.Rect(x_dir, y, largura_botao, altura_botao)
        self.botao_voltar = pygame.Rect(x_dir + largura_botao + ESPACO, y, largura_botao, altura_botao)

    def abrir(self, jogador):
        self.jogador_id = jogador["id"]
        self.selecionada = None
        self.rolagem = 0
        self.focado = 0
        self.campo_pergunta.limpar()
        self.campo_resposta.limpar()
        self._avisar("")
        self._recarregar()

    def _recarregar(self):
        self.cartas = banco.listar(self.jogador_id)
        self._rolar(0)

    def _avisar(self, texto, ok=False):
        self.mensagem = texto
        self.mensagem_ok = ok

    def _campo_focado(self):
        return self.campo_resposta if self.focado == 1 else self.campo_pergunta

    def _rolar(self, delta):
        maximo = max(0, len(self.cartas) - self.visiveis)
        self.rolagem = min(max(0, self.rolagem + delta), maximo)

    def _adicionar(self):
        pergunta = self.campo_pergunta.texto.strip()
        resposta = self.campo_resposta.texto.strip()
        if not pergunta or not resposta:
            self._avisar("Preencha a pergunta e a resposta.")
        elif not banco.adicionar(self.jogador_id, pergunta, resposta):
            self._avisar("Você já tem um card com essa pergunta.")
        else:
            self.campo_pergunta.limpar()
            self.campo_resposta.limpar()
            self.focado = 0
            self.rolagem = 0
            self._recarregar()
            self._avisar("Card adicionado!", ok=True)

    def _apagar(self):
        if self.selecionada is None:
            self._avisar("Clique em um card da lista para apagar.")
            return
        banco.apagar(self.jogador_id, self.selecionada)
        self.selecionada = None
        self._recarregar()
        self._avisar("Card apagado.", ok=True)

    def _jogar(self):
        if len(self.cartas) < MINIMO_PARA_JOGAR:
            self._avisar("Crie pelo menos um card para jogar.")
            return None
        return "jogar"

    def _rect_item(self, posicao):
        return pygame.Rect(self.lista.x, self.lista.y + posicao * self.alt_item,
                           self.lista.width, self.alt_item - 4)

    def _clique(self, pos):
        if self.campo_pergunta.rect.collidepoint(pos):
            self.focado = 0
        elif self.campo_resposta.rect.collidepoint(pos):
            self.focado = 1
        elif self.botao_adicionar.collidepoint(pos):
            self._adicionar()
        elif self.botao_apagar.collidepoint(pos):
            self._apagar()
        elif self.botao_jogar.collidepoint(pos):
            return self._jogar()
        elif self.botao_voltar.collidepoint(pos):
            return "voltar"
        else:
            visiveis = self.cartas[self.rolagem:self.rolagem + self.visiveis]
            for posicao, carta in enumerate(visiveis):
                if self._rect_item(posicao).collidepoint(pos):
                    self.selecionada = carta["id"]
        return None

    def tratar_evento(self, evento):
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                return "voltar"
            if evento.key == pygame.K_TAB:
                self.focado = 1 - self.focado
            elif evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                if self.focado == 0:
                    self.focado = 1
                else:
                    self._adicionar()
            elif evento.key == pygame.K_BACKSPACE:
                self._campo_focado().apagar()
            else:
                self._campo_focado().digitar(evento.unicode)
        elif evento.type == pygame.MOUSEWHEEL:
            self._rolar(-evento.y)
        elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            return self._clique(evento.pos)
        return None

    def _rotulo(self, tela, texto, posicao):
        tela.blit(renderizar(self.fonte, texto, COR_CREME), posicao)

    def desenhar(self, tela, clima=None):
        desenhar_fundo(tela, imagem_bg_cadastro, clima)

        tela.blit(renderizar(self.fonte_titulo, "Meus flashcards", COR_TITULO), self.pos_titulo)

        self._desenhar_lista(tela)

        self._rotulo(tela, "Pergunta", self.pos_rotulo_pergunta)
        self.campo_pergunta.desenhar(tela, self.fonte, self.focado == 0)
        self._rotulo(tela, "Resposta", self.pos_rotulo_resposta)
        self.campo_resposta.desenhar(tela, self.fonte, self.focado == 1)

        if self.mensagem:
            cor = COR_SUCESSO_TEXTO if self.mensagem_ok else COR_ERRO_TEXTO
            largura = self.painel.right - MARGEM - self.pos_mensagem[0]
            tela.blit(renderizar(self.fonte, _cortar(self.mensagem, self.fonte, largura), cor),
                      self.pos_mensagem)

        pode_jogar = len(self.cartas) >= MINIMO_PARA_JOGAR
        _desenhar_botao(tela, self.fonte, self.botao_adicionar, "Adicionar", COR_CERTA)
        _desenhar_botao(tela, self.fonte, self.botao_apagar, "Apagar", CORES_ALTERNATIVAS[3])
        _desenhar_botao(tela, self.fonte, self.botao_jogar, "Jogar", CORES_ALTERNATIVAS[0] if pode_jogar else COR_NEUTRA)
        _desenhar_botao(tela, self.fonte, self.botao_voltar, "Voltar", COR_BOTAO_NEUTRO)

    def _desenhar_lista(self, tela):
        self._rotulo(tela, f"Seus cards ({len(self.cartas)})", self.pos_cabecalho_lista)
        desenhar_bloco_pixel(tela, self.lista, COR_PAPEL, COR_MADEIRA_ESCURA, canto=esc(4), espessura=esc(4), sombra=0)

        if not self.cartas:
            tela.blit(self.fonte.render("Nenhum card ainda.", True, COR_NEUTRA),
                      (self.lista.x + PREENCHIMENTO, self.lista.y + PREENCHIMENTO))
            return

        largura_texto = self.lista.width - 2 * PREENCHIMENTO - FAIXA_ITEM
        visiveis = self.cartas[self.rolagem:self.rolagem + self.visiveis]
        for posicao, carta in enumerate(visiveis):
            rect = self._rect_item(posicao).inflate(-8, 0)
            cor = CORES_ALTERNATIVAS[(self.rolagem + posicao) % len(CORES_ALTERNATIVAS)]
            selecionada = carta["id"] == self.selecionada
            if selecionada:
                pygame.draw.rect(tela, cor, rect, border_radius=6)
            else:
                pygame.draw.rect(tela, cor, (rect.x, rect.y, FAIXA_ITEM, rect.height), border_radius=4)
            texto = _cortar(carta["pergunta"], self.fonte, largura_texto)
            tela.blit(self.fonte.render(texto, True, BRANCO if selecionada else COR_TINTA),
                      (rect.x + FAIXA_ITEM + PREENCHIMENTO, rect.y + 5))


class TelaCarta:
    def __init__(self):
        self.fonte = FontePixel(40)
        self.fonte_titulo = FontePixel(36)
        self.campo = CampoTexto("Sua resposta", 0, 0, max_len=LIMITE_RESPOSTA)
        self.carta = None
        self.acertou = None
        self.aberta_em = 0
        self.escurecer = pygame.Surface((LARGURA_TELA, ALTURA_TELA), pygame.SRCALPHA)
        self.escurecer.fill((0, 0, 0, 170))

    def abrir(self, carta):
        self.carta = carta
        self.acertou = None
        self.aberta_em = pygame.time.get_ticks()
        self.campo.limpar()
        self.campo.foco = True
        self._montar_layout()

    def _montar_layout(self):
        altura_linha = self.fonte.get_linesize()
        largura_painel = int(LARGURA_TELA * 0.8)
        largura_texto = largura_painel - 2 * MARGEM
        largura_linha = largura_texto - 2 * PREENCHIMENTO

        self.linhas_pergunta = quebrar_linhas(self.carta["enunciado"], self.fonte, largura_linha)
        self.linhas_resposta = quebrar_linhas(self.carta["resposta"], self.fonte, largura_linha)

        y = MARGEM + self.fonte_titulo.get_linesize() + ESPACO
        caixa = pygame.Rect(MARGEM, y, largura_texto, len(self.linhas_pergunta) * altura_linha + 2 * PREENCHIMENTO)
        y = caixa.bottom + ESPACO + ESPACO_ROTULO
        y_campo = y
        y += ALTURA_CAMPO + 2 * ESPACO
        faixa = pygame.Rect(MARGEM, y, largura_texto, (1 + len(self.linhas_resposta)) * altura_linha + 2 * PREENCHIMENTO)
        y = faixa.bottom + ESPACO
        self.y_aviso = y
        altura_painel = y + altura_linha + MARGEM

        self.painel = pygame.Rect((LARGURA_TELA - largura_painel) // 2,
                                  (ALTURA_TELA - altura_painel) // 2,
                                  largura_painel, altura_painel)
        self.caixa = caixa.move(self.painel.topleft)
        self.faixa = faixa.move(self.painel.topleft)
        self.campo.rect = pygame.Rect(self.painel.x + MARGEM, self.painel.y + y_campo,
                                      largura_texto, ALTURA_CAMPO)

    def tratar_evento(self, evento):
        """Devolve "acertou" ou "errou" depois que o jogador responde e continua."""
        if pygame.time.get_ticks() - self.aberta_em < ATRASO_ENTRADA_MS:
            return None

        enter = evento.type == pygame.KEYDOWN and evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER)

        if self.acertou is None:
            if enter:
                if self.campo.texto.strip():
                    self.acertou = respostas_iguais(self.campo.texto, self.carta["resposta"])
                    self.campo.foco = False
            else:
                self.campo.tratar_evento(evento)
                self.campo.foco = True
            return None

        if enter or evento.type == pygame.MOUSEBUTTONDOWN:
            return "acertou" if self.acertou else "errou"
        return None

    def _desenhar_resultado(self, tela):
        altura_linha = self.fonte.get_linesize()
        if self.acertou:
            faixa = self.faixa.copy()
            faixa.height = altura_linha + 2 * PREENCHIMENTO
            desenhar_botao_colorido(tela, faixa, COR_CERTA)
            titulo, linhas = "Acertou!", []
        else:
            desenhar_botao_colorido(tela, self.faixa, COR_ERRADA)
            titulo, linhas = "Errou! Resposta certa:", self.linhas_resposta

        x, y = self.faixa.x + PREENCHIMENTO, self.faixa.y + PREENCHIMENTO
        tela.blit(renderizar(self.fonte, titulo, BRANCO), (x, y))
        for texto in linhas:
            y += altura_linha
            tela.blit(renderizar(self.fonte, texto, COR_TITULO), (x, y))

    def desenhar(self, tela):
        altura_linha = self.fonte.get_linesize()
        tela.blit(self.escurecer, (0, 0))
        desenhar_placa(tela, self.painel, veios=False)

        tela.blit(renderizar(self.fonte_titulo, "PERGUNTA", COR_TITULO), (self.painel.x + MARGEM, self.painel.y + MARGEM))

        desenhar_papel(tela, self.caixa)
        y = self.caixa.y + PREENCHIMENTO
        for texto in self.linhas_pergunta:
            tela.blit(self.fonte.render(texto, True, COR_TINTA), (self.caixa.x + PREENCHIMENTO, y))
            y += altura_linha

        self.campo.desenhar(tela)

        if self.acertou is None:
            aviso = "Digite a resposta e aperte Enter"
        else:
            self._desenhar_resultado(tela)
            aviso = "Clique ou Enter para continuar"
        tela.blit(renderizar(self.fonte, aviso, COR_DICA), (self.painel.x + MARGEM, self.painel.y + self.y_aviso))


