# Arquivo responsável por administrar o funcionamento do jogo

import pygame

from game.configuracoes import LARGURA_TELA, ALTURA_TELA, TITULO_JOGO, FULLSCREEN, FPS
from game import catalogo
from game.database import db, flashcards_db, loja_db
from game.database.db import criar_tabelas, salvar_pontuacao, get_top5_pontuacao
from game.database.flashcards_db import criar_tabelas_flashcards
from game.database.perguntas_db import criar_tabelas_perguntas, semear_iniciais, sortear, registrar_resposta
from game.elements.personagem import Personagem
from game.elements.chao import Chao, GerenciadorChao
from game.elements.vilao import Vilao
from game.elements.cerebro import Cerebro
from game.elements.powerups import PowerUps, ACERTOS_PARA_POWERUP
from game.elements.vidas import Vidas
from game.elements.clima import Clima
from game.temas import tema, caminho_fundo, caminho_chao, caminhos_obstaculos, caminhos_viloes
from game.elements.corredor import Corredor
from game.som import Som
from game.render import carregar_fundo, desenhar_menu, desenhar_jogo, desenhar_gameover, imagem_menu, imagem_gameover, mensagem_gameover
from game.ui.botao import (botao_jogar, botao_modos, botao_config, botao_ranking, botao_sair, botao_reiniciar,
                        botao_sair_gameover, botao_menu, botao_flashcards, botao_loja, botao_estatisticas)
from game.ui.conta import TelaConfig, TelaLogin, TelaCadastro
from game.ui.perfil import TelaTrocarSenha, TelaTrocarUsuario, TelaApagarConta
from game.ui.pergunta import TelaPergunta
from game.ui.flashcard import TelaFlashcards, TelaCarta
from game.ui.modos import TelaModos
from game.ui.escolha_powerup import TelaPowerUp
from game.ui.estatisticas import TelaEstatisticas
from game.ui.loja import TelaLoja
from game.ui.ranking import TelaRanking
from game.ui.tutorial import TelaTutorial
from game.ui.pausa import TelaPausa
from game.ui.resumo import PainelResumo
from game.ui.controles import BotoesJogo


# valores da partida (início e reinício usam os mesmos)
VELOCIDADE_CHAO = 6
VELOCIDADE_MAXIMA = 10
DISTANCIA_POR_NIVEL = 6000
PONTOS_POR_DIFICULDADE = 50
COMBO_MAXIMO = 5
ESPACO_MINIMO = 150
ESPACO_MAXIMO = 270
ALTURA_PERSONAGEM = 120
ALTURA_PERSONAGEM_SKIN = int(ALTURA_PERSONAGEM * 1.2)
ALTURA_VILAO = 90
ALTURA_CEREBRO = 60
PONTOS_ACERTO = 5
PONTOS_ERRO = 2
MOEDAS_POR_ACERTO = 2
FATOR_CAMERA_LENTA = 0.6
FRAMES_IMUNIDADE_POS_PERGUNTA = 90
X_PERSONAGEM = 150


MODO_INICIAL = "flashcard"

ESTADOS_CONTA = ("config", "login", "cadastro", "trocar_senha", "trocar_usuario", "apagar_conta")
ESTADOS_PARTIDA = ("jogar", "pergunta", "tutorial", "powerup", "carta", "pausa")
ESTADOS_SEM_DIGITACAO = ("menu", "jogar", "pausa", "gameover", "rank", "modos", "loja", "estatisticas",
                        "pergunta", "powerup")


class Motor:
    def __init__(self):
        flags = pygame.FULLSCREEN if FULLSCREEN else 0
        self.tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA), flags)
        pygame.display.set_caption(TITULO_JOGO)

        criar_tabelas()
        criar_tabelas_perguntas()
        semear_iniciais()
        criar_tabelas_flashcards()
        loja_db.criar_tabelas_loja()

        self.watch = pygame.time.Clock()
        self.clima = Clima()
        self.rodando = True
        self.pontos = 0
        self.vistas_por_modo = {}
        self.estado = "menu"

        # jogador logado: None ou {"id": ..., "usuario": ...}
        self.jogador = None
        self.origem_login = "menu"
        self.apos_login = None
        self.tutorial_visitante = set()
        self.fundo_atual = None

        # telas de conta
        self.tela_config = TelaConfig()
        self.tela_login = TelaLogin()
        self.tela_cadastro = TelaCadastro()
        self.tela_trocar_senha = TelaTrocarSenha()
        self.tela_trocar_usuario = TelaTrocarUsuario()
        self.tela_apagar_conta = TelaApagarConta()
        self.tela_pergunta = TelaPergunta()
        self.tela_flashcards = TelaFlashcards()
        self.tela_carta = TelaCarta()
        self.tela_modos = TelaModos()
        self.tela_powerup = TelaPowerUp()
        self.tela_estatisticas = TelaEstatisticas()
        self.tela_loja = TelaLoja()
        self.tela_tutorial = TelaTutorial()
        self.tela_pausa = TelaPausa()
        self.tela_ranking = TelaRanking()
        self.painel_resumo = PainelResumo()
        self.controles = BotoesJogo()
        self.resumo = {}
        self.som = Som()
        self.usar_meus_cards = False
        self.powerups = PowerUps()
        self.vidas = Vidas()

        # telas de formulário, desenhadas pelo nome do estado
        self.formularios = {
            "login": self.tela_login,
            "cadastro": self.tela_cadastro,
            "trocar_senha": self.tela_trocar_senha,
            "trocar_usuario": self.tela_trocar_usuario,
            "apagar_conta": self.tela_apagar_conta,
        }

        self.personagem = Personagem(
            largura_tela=LARGURA_TELA,
            altura_tela=ALTURA_TELA,
            x=X_PERSONAGEM, y=0,
            altura=ALTURA_PERSONAGEM,
            caminhos_imagens=tema(MODO_INICIAL)["personagem"]
        )
        self.corredor = Corredor(self.personagem, LARGURA_TELA)
        self.imagem_cerebro = Cerebro.carregar_imagem(ALTURA_CEREBRO)
        self.escolher_modo(MODO_INICIAL)
        self.iniciar_partida()

    @property
    def logado(self):
        return self.jogador is not None

    @property
    def id_jogador(self):
        return self.jogador["id"] if self.jogador else None

    def escolher_modo(self, modo):
        self.modo = modo
        self.viloes = [Vilao.carregar_imagens(caminhos, ALTURA_VILAO) for caminhos in caminhos_viloes(modo)]
        self.imagem_tile = Chao.carregar_tile(caminho_chao(modo))
        self.imagens_obstaculo = [Chao.carregar_obstaculo(caminho) for caminho in caminhos_obstaculos(modo)]

    def aplicar_visual(self):
        """Personagem e fundo do modo, ou os da skin que o jogador equipou na loja."""
        equipados = loja_db.equipados(self.id_jogador) if self.logado else {}
        skin = equipados.get(self.modo)
        personagem = catalogo.personagem(skin)

        self.altura_personagem = ALTURA_PERSONAGEM_SKIN if personagem else ALTURA_PERSONAGEM
        self.personagem.trocar_imagens(personagem or tema(self.modo)["personagem"], self.altura_personagem)
        caminho = catalogo.fundo(skin) or caminho_fundo(self.modo)
        if caminho != self.fundo_atual:
            self.fundo = carregar_fundo(caminho)
            self.fundo_atual = caminho

    def iniciar_partida(self):
        self.aplicar_visual()
        self.pontos = 0
        self.combo = 0
        self.distancia = 0
        self.acertos = 0
        self.erros = 0
        self.melhor_combo = 0
        self.pergunta_atual = None
        self.perguntas_feitas = []
        self.powerups.resetar()
        self.vidas.resetar()

        self.gerenciador_chao = GerenciadorChao(
            largura_tela=LARGURA_TELA,
            altura_tela=ALTURA_TELA,
            velocidade=VELOCIDADE_CHAO,
            espaco_minimo=ESPACO_MINIMO,
            espaco_maximo=ESPACO_MAXIMO,
            viloes=self.viloes,
            imagem_cerebro=self.imagem_cerebro,
            imagem_tile=self.imagem_tile,
            imagens_obstaculo=self.imagens_obstaculo
        )

        y_inicial = (ALTURA_TELA - self.gerenciador_chao.altura_do_chao_inicial) - self.altura_personagem
        self.personagem.resetar(X_PERSONAGEM, y_inicial)

    def comecar_partida(self):
        self.iniciar_partida()
        if self.tutorial_visto():
            self.estado = "jogar"
        else:
            self.tela_tutorial.abrir()
            self.estado = "tutorial"

    def tutorial_visto(self):
        if self.logado:
            return db.tutorial_visto(self.id_jogador, self.modo)
        return self.modo in self.tutorial_visitante

    def fechar_tutorial(self):
        if self.logado:
            db.marcar_tutorial_visto(self.id_jogador, self.modo)
        else:
            self.tutorial_visitante.add(self.modo)
        self.estado = "jogar"

    def desenhar_partida(self):
        desenhar_jogo(self.tela, self.fundo, self.clima, self.personagem, self.gerenciador_chao,
                    self.pontos, self.powerups, min(self.combo, COMBO_MAXIMO), self.vidas)
        self.controles.desenhar(self.tela, self.som)

    def jogo(self):
        while self.rodando:
            self.watch.tick(FPS)

            self.capturar_eventos()
            self.clima.atualizar()
            self.som.musica("jogo" if self.estado in ESTADOS_PARTIDA else "menu")

            if self.estado == "menu":
                self.corredor.atualizar()
                desenhar_menu(self.tela, self.clima, self.jogador, self.corredor)

            elif self.estado == "jogar":
                self.atualizar_jogo()
                self.desenhar_partida()

            elif self.estado == "pergunta":
                self.tela_pergunta.atualizar()
                self.desenhar_partida()
                self.tela_pergunta.desenhar(self.tela)

            elif self.estado == "tutorial":
                self.desenhar_partida()
                self.tela_tutorial.desenhar(self.tela)

            elif self.estado == "pausa":
                self.desenhar_partida()
                self.tela_pausa.desenhar(self.tela)

            elif self.estado == "powerup":
                self.desenhar_partida()
                self.tela_powerup.desenhar(self.tela)

            elif self.estado == "carta":
                self.desenhar_partida()
                self.tela_carta.desenhar(self.tela)

            elif self.estado == "flashcards":
                self.tela_flashcards.desenhar(self.tela, self.clima)

            elif self.estado == "modos":
                chegou = self.tela_modos.atualizar()
                self.tela_modos.desenhar(self.tela)
                if chegou:
                    self.selecionar_modo(chegou)

            elif self.estado == "gameover":
                desenhar_gameover(self.tela, imagem_gameover, mensagem_gameover)
                self.painel_resumo.desenhar(self.tela, self.resumo)

            elif self.estado == "rank":
                self.tela_ranking.desenhar(self.tela, self.clima)

            elif self.estado == "config":
                self.tela_config.desenhar(self.tela, self.jogador, self.clima)

            elif self.estado == "estatisticas":
                self.tela_estatisticas.desenhar(self.tela, self.clima)

            elif self.estado == "loja":
                self.tela_loja.desenhar(self.tela, self.clima)

            elif self.estado in self.formularios:
                self.formularios[self.estado].desenhar(self.tela, self.clima)

            pygame.display.update()


    def abrir_config(self, mensagem=""):
        self.tela_config.mensagem = mensagem
        self.estado = "config"

    def exigir_login(self, destino, mensagem):
        """Visitante vai para a conta e, depois de entrar, segue para a tela que queria abrir."""
        if self.logado:
            return False
        self.apos_login = destino
        self.abrir_config(mensagem)
        return True

    def abrir_modos(self):
        if self.exigir_login("modos", "Entre ou cadastre-se para escolher um modo."):
            return
        self.tela_modos.abrir(self.modo)
        self.estado = "modos"

    def abrir_loja(self):
        if self.exigir_login("loja", "Entre ou cadastre-se para usar a loja."):
            return
        self.tela_loja.abrir(self.jogador)
        self.estado = "loja"

    def abrir_estatisticas(self):
        if self.exigir_login("estatisticas", "Entre ou cadastre-se para ver suas estatísticas."):
            return
        self.tela_estatisticas.abrir(self.jogador)
        self.estado = "estatisticas"

    def abrir_flashcards(self):
        if self.exigir_login("flashcards", "Entre ou cadastre-se para criar seus flashcards."):
            return
        self.tela_flashcards.abrir(self.jogador)
        self.estado = "flashcards"

    def abrir_login(self, mensagem=None, origem="menu", sucesso=False):
        self.origem_login = origem
        self.tela_login.resetar(mensagem, sucesso)
        self.estado = "login"

    def selecionar_modo(self, modo):
        self.escolher_modo(modo)
        self.usar_meus_cards = False
        self.comecar_partida()

    def abrir_cadastro(self):
        self.tela_cadastro.resetar()
        self.estado = "cadastro"

    def abrir_perfil(self, estado):
        self.formularios[estado].abrir(self.jogador)
        self.estado = estado

    def tratar_evento_conta(self, evento):
        if self.estado == "config":
            acao = self.tela_config.tratar_evento(evento, self.jogador)

            if acao == "login":
                self.abrir_login(origem="config")
            elif acao == "cadastro":
                self.abrir_cadastro()
            elif acao in ("trocar_senha", "trocar_usuario", "apagar_conta"):
                self.abrir_perfil(acao)
            elif acao == "logout":
                self.jogador = None
                self.abrir_config()
            elif acao == "voltar":
                self.estado = "menu"

        elif self.estado == "login":
            acao = self.tela_login.tratar_evento(evento)

            if acao == "logado":
                self.jogador = self.tela_login.jogador_logado
                destino, self.apos_login = self.apos_login, None
                if destino:
                    getattr(self, f"abrir_{destino}")()
                else:
                    self.estado = "menu"
            elif acao == "voltar":
                self.estado = self.origem_login

        elif self.estado == "cadastro":
            acao = self.tela_cadastro.tratar_evento(evento)

            if acao == "cadastrado":
                self.abrir_login("Conta criada com sucesso!", origem="config", sucesso=True)
                # já preenche o usuário e deixa o cursor na senha
                self.tela_login.campo_usuario.texto = self.tela_cadastro.usuario_criado
                self.tela_login.focar_campo(self.tela_login.campo_senha)
            elif acao == "voltar":
                self.abrir_config()

        elif self.estado == "trocar_senha":
            acao = self.tela_trocar_senha.tratar_evento(evento)

            if acao == "senha_alterada":
                self.abrir_config("Senha alterada com sucesso!")
            elif acao == "voltar":
                self.abrir_config()

        elif self.estado == "trocar_usuario":
            acao = self.tela_trocar_usuario.tratar_evento(evento)

            if acao == "usuario_alterado":
                self.jogador["usuario"] = self.tela_trocar_usuario.novo_usuario
                self.abrir_config("Nome de usuário alterado com sucesso!")
            elif acao == "voltar":
                self.abrir_config()

        elif self.estado == "apagar_conta":
            acao = self.tela_apagar_conta.tratar_evento(evento)

            if acao == "conta_apagada":
                self.jogador = None
                self.abrir_config("Sua conta foi apagada.")
            elif acao == "voltar":
                self.abrir_config()

    def capturar_eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self.encerrar_jogo()

            if (evento.type == pygame.KEYDOWN and evento.key == pygame.K_m
                    and self.estado in ESTADOS_SEM_DIGITACAO):
                self.som.alternar_tudo()
                continue

            if self.estado == "flashcards":
                acao = self.tela_flashcards.tratar_evento(evento)
                if acao == "voltar":
                    self.estado = "menu"
                elif acao == "jogar":
                    self.escolher_modo("flashcard")
                    self.usar_meus_cards = True
                    self.comecar_partida()
                continue

            if self.estado == "loja":
                if self.tela_loja.tratar_evento(evento) == "voltar":
                    self.estado = "menu"
                continue

            if self.estado == "tutorial":
                if self.tela_tutorial.tratar_evento(evento):
                    self.fechar_tutorial()
                continue

            if self.estado == "pausa":
                acao = self.tela_pausa.tratar_evento(evento)
                if acao == "continuar":
                    self.estado = "jogar"
                elif acao == "reiniciar":
                    self.comecar_partida()
                elif acao == "menu":
                    self.estado = "menu"
                continue

            if self.estado == "rank":
                if self.tela_ranking.tratar_evento(evento) == "voltar":
                    self.estado = "menu"
                continue

            if self.estado == "estatisticas":
                if self.tela_estatisticas.tratar_evento(evento) == "voltar":
                    self.estado = "menu"
                continue

            if self.estado == "modos":
                acao = self.tela_modos.tratar_evento(evento)
                if acao == "voltar":
                    self.estado = "menu"
                elif acao:
                    self.selecionar_modo(acao)
                continue

            if self.estado == "powerup":
                chave = self.tela_powerup.tratar_evento(evento)
                if chave:
                    self.ativar_powerup(chave)
                continue

            if self.estado == "carta":
                resultado = self.tela_carta.tratar_evento(evento)
                if resultado:
                    self.responder_pergunta(resultado)
                continue

            if self.estado in ESTADOS_CONTA:
                self.tratar_evento_conta(evento)
                continue

            if self.estado == "pergunta":
                resultado = self.tela_pergunta.tratar_evento(evento)
                if resultado:
                    self.responder_pergunta(resultado)
                continue

            if self.estado == "jogar" and evento.type == pygame.KEYDOWN and evento.key in (pygame.K_ESCAPE, pygame.K_p):
                self.estado = "pausa"
                continue

            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                self.encerrar_jogo()

            if evento.type == pygame.KEYDOWN and evento.key in (pygame.K_SPACE, pygame.K_UP):
                if self.estado == "jogar":
                    self.personagem.pular()
                    self.som.tocar("pulo")

            if evento.type == pygame.MOUSEBUTTONDOWN:
                if self.estado == "menu":
                    self.apos_login = None
                    if botao_jogar.clicado(evento.pos):
                        self.usar_meus_cards = False
                        self.comecar_partida()

                    elif botao_ranking.clicado(evento.pos):
                        if not self.logado:
                            self.abrir_login("Faça login para ver o seu ranking.")
                        else:
                            self.tela_ranking.abrir({"geral": get_top5_pontuacao(self.jogador["id"])})
                            self.estado = "rank"

                    elif botao_modos.clicado(evento.pos):
                        self.abrir_modos()

                    elif botao_flashcards.clicado(evento.pos):
                        self.abrir_flashcards()

                    elif botao_loja.clicado(evento.pos):
                        self.abrir_loja()

                    elif botao_estatisticas.clicado(evento.pos):
                        self.abrir_estatisticas()

                    elif botao_config.clicado(evento.pos):
                        self.abrir_config()

                    elif botao_sair.clicado(evento.pos):
                        self.rodando = False

                elif self.estado == "gameover":
                    if botao_reiniciar.clicado(evento.pos):
                        self.comecar_partida()
                    elif botao_menu.clicado(evento.pos):
                        self.estado = "menu"
                    elif botao_sair_gameover.clicado(evento.pos):
                        self.rodando = False

                elif self.estado == "jogar" and evento.button == 1:
                    acao = self.controles.clique(evento.pos)
                    if acao == "pausar":
                        self.estado = "pausa"
                    elif acao == "efeitos":
                        self.som.alternar_efeitos()
                    elif acao == "musica":
                        self.som.alternar_musica()

    def atualizar_jogo(self):
        self.powerups.atualizar()
        self.personagem.pulo_duplo = self.powerups.ativo("pulo_duplo")

        nivel = self.distancia // DISTANCIA_POR_NIVEL
        self.gerenciador_chao.definir_nivel(nivel)
        velocidade = min(VELOCIDADE_MAXIMA, VELOCIDADE_CHAO + nivel)
        if self.powerups.ativo("camera_lenta"):
            velocidade = round(velocidade * FATOR_CAMERA_LENTA)
        if velocidade != self.gerenciador_chao.velocidade:
            self.gerenciador_chao.definir_velocidade(velocidade)

        self.distancia += self.gerenciador_chao.velocidade
        chaos_removidos = self.gerenciador_chao.atualizar()
        self.pontos += chaos_removidos

        self.personagem.atualizar(self.gerenciador_chao.lista_chaos, self.gerenciador_chao.plataformas)
        if not self.personagem.escudo:
            self.powerups.consumir("escudo")

        moedas = self.gerenciador_chao.coletar_moedas(self.personagem.hitbox)
        if moedas:
            self.powerups.ganhar(moedas)
            self.som.tocar("moeda")

        if not self.personagem.vivo:
            self.terminar_partida()

        elif self.gerenciador_chao.coletar_cerebro(self.personagem.hitbox):
            self.abrir_pergunta()

    def terminar_partida(self):
        self.estado = "gameover"
        self.som.tocar("gameover")

        vale_ranking = self.logado and not self.usar_meus_cards
        recorde = vale_ranking and self.pontos > max(get_top5_pontuacao(self.jogador["id"]), default=0)
        self.resumo = {"pontos": self.pontos, "acertos": self.acertos, "erros": self.erros,
                    "combo": self.melhor_combo, "moedas": self.powerups.moedas, "recorde": recorde}
        if vale_ranking:
            salvar_pontuacao(self.jogador["id"], self.pontos, self.powerups.moedas)

    def abrir_pergunta(self):
        if self.usar_meus_cards:
            carta = flashcards_db.sortear(self.id_jogador, self.perguntas_feitas)
            if carta is not None:
                self.pergunta_atual = carta
                self.perguntas_feitas.append(carta["enunciado"])
                self.tela_carta.abrir(carta)
                self.estado = "carta"
                return
            self.usar_meus_cards = False

        dificuldade = min(3, 1 + self.pontos // PONTOS_POR_DIFICULDADE)
        vistas = self.vistas_por_modo.setdefault(self.modo, [])
        pergunta = sortear(self.modo, vistas, self.id_jogador, dificuldade)
        if pergunta["enunciado"] in vistas:
            vistas.clear()
        vistas.append(pergunta["enunciado"])
        self.pergunta_atual = pergunta
        self.tela_pergunta.abrir(pergunta)
        self.estado = "pergunta"

    def responder_pergunta(self, resultado):
        acertou = resultado == "acertou"
        if self.usar_meus_cards:
            flashcards_db.registrar(self.pergunta_atual["id"], acertou)
        else:
            registrar_resposta(self.id_jogador, self.pergunta_atual["id"], acertou)

        if acertou:
            self.combo += 1
            self.acertos += 1
            self.melhor_combo = max(self.melhor_combo, self.combo)
            self.som.tocar("acerto")
            self.pontos += PONTOS_ACERTO * min(self.combo, COMBO_MAXIMO)
            self.powerups.ganhar(MOEDAS_POR_ACERTO)
            self.vidas.acertar()
        else:
            self.combo = 0
            self.erros += 1
            self.som.tocar("erro")
            self.pontos = max(0, self.pontos - PONTOS_ERRO)
            self.vidas.errar()
            if self.vidas.atual == 0:
                self.terminar_partida()
                return

        if acertou and self.combo % ACERTOS_PARA_POWERUP == 0:
            self.tela_powerup.abrir()
            self.estado = "powerup"
        else:
            self.retomar_jogo()

    def retomar_jogo(self):
        self.personagem.imune = max(self.personagem.imune, FRAMES_IMUNIDADE_POS_PERGUNTA)
        self.estado = "jogar"

    def ativar_powerup(self, chave):
        self.som.tocar("powerup")
        self.powerups.ativar(chave)
        if chave == "escudo":
            self.personagem.escudo = True
        self.retomar_jogo()

    def encerrar_jogo(self):
        self.rodando = False
        pygame.quit()
        quit()



