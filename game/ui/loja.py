import pygame

from game import catalogo
from game.configuracoes import LARGURA_TELA, ALTURA_TELA, imagem_bg_cadastro
from game.database import loja_db
from game.temas import NOMES_MODOS
from game.ui.conta import desenhar_fundo
from game.ui.estilo import (COR_DICA, COR_ERRO_TEXTO, COR_NEUTRA, COR_SUCESSO_TEXTO, COR_TITULO, PALETAS,
                            desenhar_botao_pixel)
from game.ui.fontes import FontePixel, esc, renderizar
from game.ui.carrossel import lugar, suavizar
from game.ui.hud import COR_MOEDA, COR_BORDA_MOEDA
from game.ui.icones import desenhar_icone
from game.ui.seta import BotaoSeta
from game.util.cores import cores

BRANCO = (255, 255, 255)
MARGEM = esc(30)
ALTURA_CARTAO = int(ALTURA_TELA * 0.6)
LARGURA_CARTAO = int(ALTURA_CARTAO * 0.66)
CENTRO_Y = int(ALTURA_TELA * 0.53)
INTERVALO_QUADRO_MS = 180
MAXIMO_CACHE = 200
DICA = "Setas ou roda do mouse para trocar. Clique em EQUIPADO para voltar ao visual padrão."

# cor do cartão de cada modo
PALETA_MODO = {"flashcard": "azul", "computacao": "roxo", "historia": "dourado", "medvet": "verde", "letras": "vermelho"}

FONTE_TITULO = FontePixel(56)
FONTE_SALDO = FontePixel(40)
FONTE_NOME = FontePixel(38)
FONTE_MODO = FontePixel(26)
FONTE_BOTAO = FontePixel(36)
FONTE_PRECO = FontePixel(34)
FONTE_MENSAGEM = FontePixel(26)

_pad = round(0.035 * ALTURA_CARTAO)
TAMANHO_RETRATO = (LARGURA_CARTAO - 2 * _pad, round(0.60 * ALTURA_CARTAO))


def _ajustar(superficie, escala, largura_maxima=None):
    fator = escala
    if largura_maxima and superficie.get_width() * fator > largura_maxima:
        fator = largura_maxima / superficie.get_width()
    if fator == 1:
        return superficie
    tamanho = (max(1, round(superficie.get_width() * fator)), max(1, round(superficie.get_height() * fator)))
    return pygame.transform.smoothscale(superficie, tamanho)


class TelaLoja:
    def __init__(self):
        self.jogador_id = None
        self.mensagem = ""
        self.mensagem_ok = False
        self.itens = []
        self.estrelas = {}
        self.saldo = 0
        self.comprados = set()
        self.equipados = {}
        self.indice = 0
        self.posicao = 0.0
        self.retratos = {}
        self.bonecos = {}
        self.cache_bonecos = {}
        self.rects = {}
        self.rect_botao = pygame.Rect(0, 0, 0, 0)

        self.botao_voltar = BotaoSeta("esquerda", topleft=(MARGEM, MARGEM))
        self.seta_esquerda = BotaoSeta("esquerda", centro=(esc(70), CENTRO_Y))
        self.seta_direita = BotaoSeta("direita", centro=(LARGURA_TELA - esc(70), CENTRO_Y))

    def abrir(self, jogador):
        self.jogador_id = jogador["id"]
        self._avisar("")
        self._recarregar()
        self.posicao = float(self.indice)

    def _recarregar(self):
        self.saldo = loja_db.saldo(self.jogador_id)
        self.comprados = loja_db.comprados(self.jogador_id)
        self.equipados = loja_db.equipados(self.jogador_id)

        disponiveis = catalogo.disponiveis()
        self.itens = []
        self.estrelas = {}
        for modo in NOMES_MODOS:
            do_modo = sorted((i for i in disponiveis if i["modo"] == modo), key=lambda i: i["preco"])
            for numero, item in enumerate(do_modo, start=1):
                self.itens.append(item)
                self.estrelas[item["id"]] = numero
        self.indice = min(self.indice, max(0, len(self.itens) - 1))

    def _avisar(self, texto, ok=False):
        self.mensagem = texto
        self.mensagem_ok = ok

    def _equipado(self, item):
        return self.equipados.get(item["modo"]) == item["id"]

    def _clicar_item(self, item):
        modo, nome = item["modo"], item["nome"]
        if self._equipado(item):
            loja_db.equipar(self.jogador_id, modo, None)
            self._avisar(f"{NOMES_MODOS[modo]}: visual padrão.", ok=True)
        elif item["id"] in self.comprados:
            loja_db.equipar(self.jogador_id, modo, item["id"])
            self._avisar(f"{nome} equipado!", ok=True)
        elif loja_db.comprar(self.jogador_id, item["id"], modo, item["preco"]):
            loja_db.equipar(self.jogador_id, modo, item["id"])
            self._avisar(f"{nome} comprado e equipado!", ok=True)
        else:
            self._avisar("Moedas insuficientes.")
            return
        self._recarregar()

    def _mover(self, passo):
        self.indice = min(max(0, self.indice + passo), max(0, len(self.itens) - 1))

    def tratar_evento(self, evento):
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                return "voltar"
            if evento.key in (pygame.K_LEFT, pygame.K_a):
                self._mover(-1)
            elif evento.key in (pygame.K_RIGHT, pygame.K_d):
                self._mover(1)
            elif evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER) and self.itens:
                self._clicar_item(self.itens[self.indice])
        elif evento.type == pygame.MOUSEWHEEL:
            self._mover(-evento.y)
        elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if self.botao_voltar.clicado(evento.pos):
                return "voltar"
            if self.seta_esquerda.clicado(evento.pos):
                self._mover(-1)
            elif self.seta_direita.clicado(evento.pos):
                self._mover(1)
            elif self.itens and self.rect_botao.collidepoint(evento.pos):
                self._clicar_item(self.itens[self.indice])
            else:
                for indice, rect in self.rects.items():
                    if indice != self.indice and rect.collidepoint(evento.pos):
                        self.indice = indice
        return None

    def _retrato(self, item):
        if item["id"] not in self.retratos:
            largura, altura = TAMANHO_RETRATO
            retrato = pygame.Surface(TAMANHO_RETRATO)
            retrato.fill(COR_NEUTRA)
            cenario = catalogo.fundo(item["id"])
            if cenario:
                imagem = pygame.image.load(cenario).convert()
                fator = max(largura / imagem.get_width(), altura / imagem.get_height())
                tamanho = (round(imagem.get_width() * fator), round(imagem.get_height() * fator))
                imagem = pygame.transform.smoothscale(imagem, tamanho)
                retrato.blit(imagem, ((largura - tamanho[0]) // 2, (altura - tamanho[1]) // 2))
            self.retratos[item["id"]] = retrato
        return self.retratos[item["id"]]

    def _boneco(self, item, quadro, altura):
        chave = (item["id"], quadro, altura)
        if chave not in self.cache_bonecos:
            if item["id"] not in self.bonecos:
                self.bonecos[item["id"]] = [pygame.image.load(c).convert_alpha() for c in catalogo.personagem(item["id"])]
            imagem = self.bonecos[item["id"]][quadro % 3]
            largura = round(imagem.get_width() * altura / imagem.get_height())
            if len(self.cache_bonecos) > MAXIMO_CACHE:
                self.cache_bonecos.clear()
            self.cache_bonecos[chave] = pygame.transform.smoothscale(imagem, (largura, altura))
        return self.cache_bonecos[chave]

    def _status(self, item, saldo_ok):
        if self._equipado(item):
            return "EQUIPADO", "dourado"
        if item["id"] in self.comprados:
            return "EQUIPAR", "azul"
        return "COMPRAR", "verde" if saldo_ok else "vermelho"

    def _desenhar_preco(self, tela, retrato, preco, escala):
        valor = _ajustar(renderizar(FONTE_PRECO, str(preco), BRANCO, PALETAS["marinho"][0]), escala)
        raio = valor.get_height() // 3
        folga = max(2, round(esc(8) * escala))
        selo = pygame.Rect(0, 0, 2 * raio + valor.get_width() + 3 * folga, valor.get_height() + folga)
        selo.topright = (retrato.right - folga, retrato.y + folga)
        desenhar_botao_pixel(tela, selo, PALETAS["marinho"], max(2, round(esc(3) * escala)))
        centro = (selo.x + folga + raio, selo.centery - max(1, round(esc(3) * escala)))
        pygame.draw.circle(tela, COR_MOEDA, centro, raio)
        pygame.draw.circle(tela, COR_BORDA_MOEDA, centro, raio, max(2, raio // 5))
        tela.blit(valor, valor.get_rect(midleft=(centro[0] + raio + folga // 2, centro[1])))

    def _desenhar_cartao(self, tela, indice, centro_x, escala, distancia):
        item = self.itens[indice]
        foco = indice == self.indice
        mouse = pygame.mouse.get_pos()
        w, h = round(LARGURA_CARTAO * escala), round(ALTURA_CARTAO * escala)
        rect = pygame.Rect(0, 0, w, h)
        rect.center = (centro_x, CENTRO_Y)
        self.rects[indice] = rect

        paleta = PALETAS[PALETA_MODO[item["modo"]]]
        unidade = max(2, round(esc(5) * escala))
        desenhar_botao_pixel(tela, rect, paleta, unidade)
        pad = round(0.035 * h)

        nome = _ajustar(renderizar(FONTE_NOME, item["nome"], BRANCO, paleta[0]), escala, w - 2 * pad)
        tela.blit(nome, nome.get_rect(midtop=(rect.centerx, rect.y + round(0.032 * h))))

        retrato = pygame.Rect(rect.x + pad, rect.y + round(0.135 * h), w - 2 * pad, round(0.60 * h))
        base = self._retrato(item)
        tela.blit(base if retrato.size == base.get_size() else pygame.transform.smoothscale(base, retrato.size), retrato)
        quadro = (pygame.time.get_ticks() // INTERVALO_QUADRO_MS) % 3 if foco else 0
        boneco = self._boneco(item, quadro, round(retrato.height * 0.82))
        tela.set_clip(retrato)
        tela.blit(boneco, boneco.get_rect(midbottom=(retrato.centerx, retrato.bottom - round(0.03 * retrato.height))))
        tela.set_clip(None)
        pygame.draw.rect(tela, paleta[0], retrato, max(2, round(esc(4) * escala)))

        unidade_estrela = max(2, round(esc(4) * escala))
        for n in range(self.estrelas[item["id"]]):
            desenhar_icone(tela, "estrela", (retrato.x + round(esc(26) * escala) + n * round(esc(34) * escala),
                                             retrato.y + round(esc(26) * escala)),
                        unidade_estrela, COR_MOEDA, PALETAS["marinho"][0])
        self._desenhar_preco(tela, retrato, item["preco"], escala)

        modo = _ajustar(renderizar(FONTE_MODO, NOMES_MODOS[item["modo"]], paleta[3], paleta[0]), escala, w - 2 * pad)
        tela.blit(modo, modo.get_rect(midtop=(rect.centerx, rect.y + round(0.752 * h))))

        botao = pygame.Rect(rect.x + pad, rect.y + round(0.845 * h), w - 2 * pad, round(0.115 * h))
        texto, nome_paleta = self._status(item, self.saldo >= item["preco"])
        if foco and botao.collidepoint(mouse):
            nome_paleta = "verde"
        desenhar_botao_pixel(tela, botao, PALETAS[nome_paleta], max(2, round(esc(4) * escala)))
        rotulo = _ajustar(renderizar(FONTE_BOTAO, texto, BRANCO, PALETAS[nome_paleta][0]), escala, botao.width - 2 * pad)
        tela.blit(rotulo, rotulo.get_rect(center=(botao.centerx, botao.centery - round(esc(5) * escala))))

        if foco:
            self.rect_botao = botao
            if rect.collidepoint(mouse):
                pygame.draw.rect(tela, cores['verde-logo'], rect.inflate(2 * esc(8), 2 * esc(8)), esc(5))
        else:
            sombra = pygame.Surface(rect.size, pygame.SRCALPHA)
            sombra.fill((0, 0, 0, min(150, round(110 * abs(distancia)))))
            tela.blit(sombra, rect)

    def _desenhar_topo(self, tela):
        self.botao_voltar.desenhar(tela)
        titulo = renderizar(FONTE_TITULO, "LOJA DE SKINS", COR_TITULO)
        tela.blit(titulo, titulo.get_rect(center=(LARGURA_TELA // 2, MARGEM + self.botao_voltar.rect.height // 2)))

        valor = renderizar(FONTE_SALDO, str(self.saldo), BRANCO, PALETAS["dourado"][0])
        raio = valor.get_height() // 3
        selo = pygame.Rect(0, 0, 2 * raio + valor.get_width() + esc(50), self.botao_voltar.rect.height)
        selo.topright = (LARGURA_TELA - MARGEM, MARGEM)
        desenhar_botao_pixel(tela, selo, PALETAS["dourado"])
        centro = (selo.x + esc(26) + raio, selo.centery - esc(6))
        pygame.draw.circle(tela, COR_MOEDA, centro, raio)
        pygame.draw.circle(tela, COR_BORDA_MOEDA, centro, raio, max(2, raio // 5))
        tela.blit(valor, valor.get_rect(midleft=(centro[0] + raio + esc(12), centro[1])))

    def _desenhar_pontos(self, tela):
        lado, folga = esc(14), esc(10)
        total = len(self.itens) * lado + (len(self.itens) - 1) * folga
        x = (LARGURA_TELA - total) // 2
        y = int(ALTURA_TELA * 0.885)
        for i in range(len(self.itens)):
            rect = pygame.Rect(x + i * (lado + folga), y, lado, lado)
            ativo = i == self.indice
            pygame.draw.rect(tela, COR_MOEDA if ativo else PALETAS["marinho"][3], rect)
            pygame.draw.rect(tela, PALETAS["marinho"][0], rect, esc(3))

    def desenhar(self, tela, clima=None):
        desenhar_fundo(tela, imagem_bg_cadastro, clima)
        self._desenhar_topo(tela)

        if not self.itens:
            vazio = renderizar(FONTE_MENSAGEM, "Nenhuma skin disponível ainda.", COR_DICA)
            tela.blit(vazio, vazio.get_rect(center=(LARGURA_TELA // 2, CENTRO_Y)))
            return

        self.posicao = suavizar(self.posicao, self.indice)

        self.rects = {}
        visiveis = [i for i in range(len(self.itens)) if abs(i - self.posicao) <= 2.6]
        for indice in sorted(visiveis, key=lambda i: -abs(i - self.posicao)):
            distancia = indice - self.posicao
            escala, deslocamento = lugar(distancia, LARGURA_CARTAO)
            self._desenhar_cartao(tela, indice, LARGURA_TELA // 2 + round(deslocamento), escala, distancia)

        if self.indice > 0:
            self.seta_esquerda.desenhar(tela)
        if self.indice < len(self.itens) - 1:
            self.seta_direita.desenhar(tela)
        self._desenhar_pontos(tela)

        if self.mensagem:
            cor = COR_SUCESSO_TEXTO if self.mensagem_ok else COR_ERRO_TEXTO
            texto = renderizar(FONTE_MENSAGEM, self.mensagem, cor)
        else:
            texto = renderizar(FONTE_MENSAGEM, DICA, COR_DICA)
        tela.blit(texto, texto.get_rect(midbottom=(LARGURA_TELA // 2, ALTURA_TELA - esc(24))))


