import pygame
from random import randint, choice
from game.util.cores import cores
from game.elements.vilao import Vilao
from game.elements.cerebro import Cerebro
from game.elements.moeda import Moeda, FORMACOES, ALTURA_BAIXA, ESPACO as ESPACO_MOEDAS, RAIO as RAIO_MOEDA


class Chao:
    LARGURA_OBSTACULO = 110
    ALTURA_OBSTACULO = 50
    MARGEM_INICIO = 140
    MARGEM_INICIO_VILAO = 220
    MARGEM_FIM = 160
    AFUNDAR_OBSTACULO = 2
    CHANCE_OBSTACULO = 45
    CHANCE_VILAO = 25
    CHANCE_OBSTACULO_MAXIMA = 55
    CHANCE_VILAO_MAXIMA = 35
    AUMENTO_OBSTACULO = 3
    AUMENTO_VILAO = 2
    CHANCE_CEREBRO = 50
    CHANCE_MOEDAS = 55
    MARGEM_MOEDAS = 60
    ALTURA_CEREBRO_ACIMA = 140

    def __init__(self, x, y, largura, altura, velocidade, imagem_tile, imagens_obstaculo):
        self.rect = pygame.Rect(x, y, largura, altura)
        self.velocidade = velocidade
        self.imagem = Chao._montar_imagem(largura, altura, imagem_tile)
        self.imagens_obstaculo = imagens_obstaculo
        self.imagem_obstaculo = None

        # obstáculo ou vilão em cima da plataforma (None = sem nenhum)
        self.obstaculo = None
        self.deslocamento_obstaculo = 0
        self.vilao = None
        self.deslocamento_vilao = 0
        self.cerebro = None
        self.deslocamento_cerebro = 0
        self.moedas = []

    @staticmethod
    def carregar_tile(caminho):
        return pygame.image.load(caminho).convert()

    @staticmethod
    def carregar_obstaculo(caminho):
        imagem = pygame.image.load(caminho).convert()
        imagem.set_colorkey(imagem.get_at((0, 0)))
        imagem = imagem.convert_alpha()
        imagem = imagem.subsurface(imagem.get_bounding_rect()).copy()
        return pygame.transform.scale(imagem, (Chao.LARGURA_OBSTACULO, Chao.ALTURA_OBSTACULO))

    @staticmethod
    def _montar_imagem(largura, altura, tile):
        imagem = pygame.Surface((largura, altura))
        for x in range(0, largura, tile.get_width()):
            for y in range(0, altura, tile.get_height()):
                imagem.blit(tile, (x, y))
        return imagem

    def criar_obstaculo(self):
        largura = Chao.LARGURA_OBSTACULO
        altura = Chao.ALTURA_OBSTACULO

        # faixa em que o obstáculo pode nascer, respeitando as duas margens
        x_min = self.rect.x + self.MARGEM_INICIO
        x_max = self.rect.right - self.MARGEM_FIM - largura
        if x_max < x_min:
            return  # plataforma curta demais

        x = randint(x_min, x_max)
        y = self.rect.top - altura + self.AFUNDAR_OBSTACULO
        self.obstaculo = pygame.Rect(x, y, largura, altura)
        self.imagem_obstaculo = choice(self.imagens_obstaculo)
        self.deslocamento_obstaculo = x - self.rect.x

    def criar_vilao(self, imagens):
        largura = imagens[0].get_width()

        x_min = self.rect.x + self.MARGEM_INICIO_VILAO
        x_max = self.rect.right - self.MARGEM_FIM - largura
        if x_max < x_min:
            return  # plataforma curta demais

        x = randint(x_min, x_max)
        self.vilao = Vilao(imagens, x, self.rect.top)
        self.deslocamento_vilao = x - self.rect.x

    def criar_cerebro(self, imagem):
        largura = imagem.get_width()

        x_min = self.rect.x + self.MARGEM_INICIO
        x_max = self.rect.right - self.MARGEM_FIM - largura
        if x_max < x_min:
            return  # plataforma curta demais

        # flutua acima da cabeça do personagem: só o pulo alcança
        x = randint(x_min, x_max)
        self.cerebro = Cerebro(imagem, x, self.rect.top - self.ALTURA_CEREBRO_ACIMA)
        self.deslocamento_cerebro = x - self.rect.x

    def criar_moedas(self):
        baixas = self.cerebro is not None
        x_min = self.rect.x + self.MARGEM_MOEDAS
        x_max = self.rect.right - self.MARGEM_MOEDAS
        formacoes = [
            f for f in FORMACOES
            if (not baixas or max(h for _, h in f) <= ALTURA_BAIXA)
            and max(p for p, _ in f) * ESPACO_MOEDAS + 2 * RAIO_MOEDA <= x_max - x_min
        ]
        if not formacoes:
            return  # plataforma curta demais

        formacao = choice(formacoes)
        largura = max(p for p, _ in formacao) * ESPACO_MOEDAS + 2 * RAIO_MOEDA
        x = randint(x_min, x_max - largura)
        for posicao, altura in formacao:
            moeda_x = x + posicao * ESPACO_MOEDAS
            self.moedas.append(Moeda(moeda_x, self.rect.top - altura - RAIO_MOEDA, moeda_x - self.rect.x))

    def mover(self):
        self.rect.x -= self.velocidade
        if self.obstaculo is not None:
            self.obstaculo.x = self.rect.x + self.deslocamento_obstaculo
        if self.vilao is not None:
            self.vilao.rect.x = self.rect.x + self.deslocamento_vilao
            self.vilao.animar()
        if self.cerebro is not None:
            self.cerebro.rect.x = self.rect.x + self.deslocamento_cerebro
        for moeda in self.moedas:
            moeda.rect.x = self.rect.x + moeda.deslocamento

    def saiu_da_tela(self):
        return self.rect.right <= 0

    def desenhar(self, tela):
        tela.blit(self.imagem, self.rect)
        if self.obstaculo is not None:
            tela.blit(self.imagem_obstaculo, self.obstaculo)
        if self.vilao is not None:
            self.vilao.desenhar(tela)
        if self.cerebro is not None:
            self.cerebro.desenhar(tela)
        for moeda in self.moedas:
            moeda.desenhar(tela)


class Plataforma(Chao):
    """Plataforma pequena que flutua: o personagem só pousa em cima dela e a atravessa por baixo e pelos lados."""
    ALTURA = 56
    LARGURA_LIVRE = (220, 320)     # só moedas ou cérebro
    LARGURA_COM_PERIGO = (340, 440)   # com vilão ou obstáculo
    ELEVACAO = (195, 225)          # altura do topo da plataforma acima do bloco de baixo
    RECUO_INICIO = 80
    RECUO_FIM = 260                # sobra de chão atrás, para o personagem cair de volta nele
    TOPO_MINIMO = 150
    CHANCE = 55
    CHANCE_MAXIMA = 75
    AUMENTO = 2
    CONTEUDOS = ("moedas", "moedas", "moedas", "moedas", "cerebro", "cerebro", "vilao", "obstaculo")

    MARGEM_INICIO = 90
    MARGEM_INICIO_VILAO = 90
    MARGEM_FIM = 40
    MARGEM_MOEDAS = 40

    def __init__(self, x, y, largura, velocidade, imagem_tile, imagens_obstaculo):
        super().__init__(x, y, largura, Plataforma.ALTURA, velocidade, imagem_tile, imagens_obstaculo)
        self.imagem = Plataforma._montar_flutuante(largura, Plataforma.ALTURA, imagem_tile)

    @staticmethod
    def _montar_flutuante(largura, altura, tile):
        """O mesmo tijolo do chão, com brilho no topo, sombra embaixo e contorno escuro."""
        imagem = Chao._montar_imagem(largura, altura, tile)
        cor = pygame.transform.average_color(tile)[:3]
        pygame.draw.rect(imagem, tuple(min(255, c + 60) for c in cor), (0, 0, largura, 6))
        pygame.draw.rect(imagem, tuple(int(c * 0.6) for c in cor), (0, altura - 10, largura, 10))
        pygame.draw.rect(imagem, tuple(int(c * 0.3) for c in cor), imagem.get_rect(), 4)
        return imagem


class GerenciadorChao:
    DEBUG_MEDIDAS = False
    ARQUIVO_LOG = './debug_chao.log'
    _fonte_debug = None
    _frame_debug = 0

    def __init__(self, largura_tela, altura_tela, velocidade,
                altura_minima=320, altura_maxima=420,
                largura_minima=400, largura_maxima=900, # 400 | 625 | 750 | 900
                espaco_minimo=50, espaco_maximo=150, viloes=None, imagem_cerebro=None,
                imagem_tile=None, imagens_obstaculo=None):
        self.largura_tela = largura_tela
        self.altura_tela = altura_tela
        self.velocidade = velocidade

        self.altura_minima = altura_minima
        self.altura_maxima = altura_maxima
        self.largura_minima = largura_minima
        self.largura_maxima = largura_maxima
        self.espaco_minimo = espaco_minimo
        self.espaco_maximo = espaco_maximo

        self.viloes = viloes
        self.imagem_cerebro = imagem_cerebro
        self.imagem_tile = imagem_tile
        self.imagens_obstaculo = imagens_obstaculo
        self.lista_chaos = []
        self.chance_obstaculo = Chao.CHANCE_OBSTACULO
        self.chance_vilao = Chao.CHANCE_VILAO
        self.chance_plataforma = Plataforma.CHANCE
        self.plataformas = []

        largura_inicial = max(350, int(self.largura_tela * 0.6))
        primeiro_chao = self.criar_chao_fixo(x=0, largura=largura_inicial, altura=self.altura_maxima)
        self.altura_do_chao_inicial = primeiro_chao.rect.height

        # preenche o resto da tela com blocos sorteados normalmente
        x = primeiro_chao.rect.right + randint(self.espaco_minimo, self.espaco_maximo)
        while x < self.largura_tela:
            novo_chao = self.criar_chao(x)
            espaco = randint(self.espaco_minimo, self.espaco_maximo)
            x = novo_chao.rect.right + espaco

    def definir_velocidade(self, velocidade):
        self.velocidade = velocidade
        for chao in self.lista_chaos + self.plataformas:
            chao.velocidade = velocidade

    def definir_nivel(self, nivel):
        self.chance_obstaculo = min(Chao.CHANCE_OBSTACULO_MAXIMA,
                                    Chao.CHANCE_OBSTACULO + nivel * Chao.AUMENTO_OBSTACULO)
        self.chance_vilao = min(Chao.CHANCE_VILAO_MAXIMA, Chao.CHANCE_VILAO + nivel * Chao.AUMENTO_VILAO)
        self.chance_plataforma = min(Plataforma.CHANCE_MAXIMA, Plataforma.CHANCE + nivel * Plataforma.AUMENTO)

    def criar_chao_fixo(self, x, largura, altura):
        y = self.altura_tela - altura
        novo_chao = Chao(x, y, largura, altura, self.velocidade, self.imagem_tile, self.imagens_obstaculo)
        self.lista_chaos.append(novo_chao)
        return novo_chao

    def criar_chao(self, x):
        # sorteia o tamanho deste bloco especificamente
        largura_sorteada = randint(self.largura_minima, self.largura_maxima)
        altura_sorteada = randint(self.altura_minima, self.altura_maxima)

        # a base do bloco fica sempre encostada no fundo da tela;
        # só o topo sobe ou desce, dependendo da altura sorteada
        y = self.altura_tela - altura_sorteada

        novo_chao = Chao(x, y, largura_sorteada, altura_sorteada, self.velocidade,
                         self.imagem_tile, self.imagens_obstaculo)
        self.lista_chaos.append(novo_chao)

        # sorteio (em %): obstáculo, vilão ou plataforma vazia
        sorteio = randint(1, 100)
        if sorteio <= self.chance_obstaculo:
            novo_chao.criar_obstaculo()
        elif self.viloes and sorteio <= self.chance_obstaculo + self.chance_vilao:
            novo_chao.criar_vilao(choice(self.viloes))

        # o cérebro é independente: pode aparecer sobre um perigo
        if self.imagem_cerebro and randint(1, 100) <= Chao.CHANCE_CEREBRO:
            novo_chao.criar_cerebro(self.imagem_cerebro)

        if randint(1, 100) <= Chao.CHANCE_MOEDAS:
            novo_chao.criar_moedas()

        self.criar_plataforma(novo_chao)
        return novo_chao

    def _sorteio_conteudo(self):
        conteudos = [c for c in Plataforma.CONTEUDOS
                     if (c != "vilao" or self.viloes) and (c != "cerebro" or self.imagem_cerebro)]
        return choice(conteudos)

    @staticmethod
    def _livre(rect, chao):
        """A plataforma não pode cobrir o que já está sobre o bloco de baixo."""
        ocupados = [m.rect for m in chao.moedas]
        ocupados += [item.rect if hasattr(item, "rect") else item
                     for item in (chao.obstaculo, chao.vilao, chao.cerebro) if item is not None]
        area = rect.inflate(40, 40)
        return not any(area.colliderect(r) for r in ocupados)

    def criar_plataforma(self, chao):
        """Às vezes cria uma plataforma flutuante sobre o bloco, a uma altura que o pulo alcança."""
        if randint(1, 100) > self.chance_plataforma:
            return

        conteudo = self._sorteio_conteudo()
        faixa = Plataforma.LARGURA_COM_PERIGO if conteudo in ("vilao", "obstaculo") else Plataforma.LARGURA_LIVRE
        largura = randint(*faixa)
        x_min = chao.rect.x + Plataforma.RECUO_INICIO
        x_max = chao.rect.right - Plataforma.RECUO_FIM - largura
        y = chao.rect.top - randint(*Plataforma.ELEVACAO)
        if x_max < x_min or y < Plataforma.TOPO_MINIMO:
            return

        for _ in range(5):
            x = randint(x_min, x_max)
            if self._livre(pygame.Rect(x, y, largura, Plataforma.ALTURA), chao):
                break
        else:
            return

        plataforma = Plataforma(x, y, largura, self.velocidade, self.imagem_tile, self.imagens_obstaculo)
        if conteudo == "moedas":
            plataforma.criar_moedas()
        elif conteudo == "cerebro":
            plataforma.criar_cerebro(self.imagem_cerebro)
        elif conteudo == "vilao":
            plataforma.criar_vilao(choice(self.viloes))
        else:
            plataforma.criar_obstaculo()
        self.plataformas.append(plataforma)

    def coletar_moedas(self, hitbox):
        """Remove as moedas tocadas pelo personagem e devolve quantas foram."""
        coletadas = 0
        for chao in self.lista_chaos + self.plataformas:
            tocadas = [m for m in chao.moedas if hitbox.colliderect(m.rect)]
            coletadas += len(tocadas)
            chao.moedas = [m for m in chao.moedas if m not in tocadas]
        return coletadas

    def coletar_cerebro(self, hitbox):
        """Remove o cérebro tocado pelo personagem e avisa se algum foi coletado."""
        for chao in self.lista_chaos + self.plataformas:
            if chao.cerebro is not None and hitbox.colliderect(chao.cerebro.rect):
                chao.cerebro = None
                return True
        return False

    def atualizar(self):
        # passo 1: move cada bloco de chão para a esquerda
        if GerenciadorChao.DEBUG_MEDIDAS:
            antes = [(c.rect.x, c.rect.width) for c in self.lista_chaos]

        for chao in self.lista_chaos:
            chao.mover()

        for plataforma in self.plataformas:
            plataforma.mover()
        self.plataformas = [p for p in self.plataformas if not p.saiu_da_tela()]

        if GerenciadorChao.DEBUG_MEDIDAS:
            self._conferir_movimento(antes)

        # passo 2: separa os blocos que ainda estão visíveis,
        # e conta quantos saíram (usado para pontuação)
        chaos_visiveis = []
        quantidade_removida = 0

        for chao in self.lista_chaos:
            if not chao.saiu_da_tela():
                chaos_visiveis.append(chao)
            else:
                quantidade_removida += 1

        self.lista_chaos = chaos_visiveis

        # passo 3: se não sobrou nenhum bloco, cria um novo do zero
        if len(self.lista_chaos) == 0:
            self.criar_chao(self.largura_tela)
            return quantidade_removida

        # passo 4: se o último bloco já apareceu por completo na tela,
        # cria o próximo bloco depois dele, com um espaço aleatório
        ultimo_chao = self.lista_chaos[-1]

        if ultimo_chao.rect.right <= self.largura_tela:
            espaco = randint(self.espaco_minimo, self.espaco_maximo)
            proximo_x = ultimo_chao.rect.right + espaco
            self.criar_chao(proximo_x)

        return quantidade_removida

    def desenhar(self, tela):
        for chao in self.lista_chaos:
            chao.desenhar(tela)
        for plataforma in self.plataformas:
            plataforma.desenhar(tela)

        if GerenciadorChao.DEBUG_MEDIDAS:
            self._desenhar_medidas(tela)

    @staticmethod
    def _registrar(mensagem):
        """Escreve no terminal e no arquivo debug_chao.log (na pasta de onde o jogo foi iniciado)."""
        linha = f"[frame {GerenciadorChao._frame_debug}] {mensagem}"
        print("[DEBUG]", linha)
        try:
            with open(GerenciadorChao.ARQUIVO_LOG, 'a', encoding='utf-8') as arq:
                arq.write(linha + "\n")
        except OSError:
            pass

    def _conferir_movimento(self, antes):
        """Registra se algum bloco andar diferente, mudar de largura ou se algum vão mudar."""
        GerenciadorChao._frame_debug += 1

        for i, (chao, (x0, w0)) in enumerate(zip(self.lista_chaos, antes)):
            if x0 - chao.rect.x != self.velocidade:
                self._registrar(f"bloco {i} andou {x0 - chao.rect.x}px (esperado {self.velocidade}px)")
            if chao.rect.width != w0:
                self._registrar(f"bloco {i} mudou de largura: {w0} -> {chao.rect.width}")

        for i in range(len(self.lista_chaos) - 1):
            vao_antes = antes[i + 1][0] - (antes[i][0] + antes[i][1])
            vao_depois = self.lista_chaos[i + 1].rect.left - self.lista_chaos[i].rect.right
            if vao_antes != vao_depois:
                self._registrar(f"vão entre blocos {i} e {i + 1} mudou: {vao_antes} -> {vao_depois}")

    def _desenhar_medidas(self, tela):
        """Mostra L = largura real de cada bloco e vão = distância até o próximo bloco (em pixels)."""
        if GerenciadorChao._fonte_debug is None:
            GerenciadorChao._fonte_debug = pygame.font.SysFont('arial', 22, bold=True)
        fonte = GerenciadorChao._fonte_debug

        for i, chao in enumerate(self.lista_chaos):
            texto = fonte.render(f"L={chao.rect.width}", True, cores['amarelo'])
            tela.blit(texto, (max(chao.rect.x, 0) + 8, chao.rect.y + 60))

            if i + 1 < len(self.lista_chaos):
                proximo = self.lista_chaos[i + 1]
                vao = proximo.rect.left - chao.rect.right
                texto = fonte.render(f"vão={vao}", True, cores['vermelho'])
                tela.blit(texto, (chao.rect.right + 4, self.altura_tela - 40))




