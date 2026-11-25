# Arquivo responsável por desenhar e renderizar as telas do jogo

import pygame

from game.util.cores import cores
from game.ui.hud import desenhar_hud
from game.ui.logo import logo_menu
from game.configuracoes import (LARGURA_TELA, ALTURA_TELA, FONTE_TITULO, FONTE_PONTOS, FONTE_MENSAGEM, imagem_menu,
                                mensagem_gameover, imagem_gameover)
from game.ui.botao import (botao_jogar, botao_modos, botao_config, botao_ranking, botao_sair, botao_reiniciar,
                        botao_sair_gameover, botao_menu, botao_flashcards, botao_loja, botao_estatisticas)

def desenhar_menu(tela, clima, jogador, corredor):
    tela.blit(imagem_menu, (0, 0))
    clima.desenhar(tela)
    corredor.desenhar(tela)

    if jogador:
        saudacao = FONTE_MENSAGEM.render(f"Oi, {jogador['usuario']}", True, cores['verde-logo'])
        tela.blit(saudacao, saudacao.get_rect(center=(LARGURA_TELA // 2, int(ALTURA_TELA * 0.265))))

    logo_menu.desenhar(tela)
    botao_jogar.desenhar(tela)
    botao_modos.desenhar(tela)
    botao_config.desenhar(tela)
    botao_ranking.desenhar(tela)
    botao_sair.desenhar(tela)
    botao_flashcards.desenhar(tela)
    botao_loja.desenhar(tela)
    botao_estatisticas.desenhar(tela)


def carregar_fundo(caminho):
    imagem = pygame.image.load(caminho).convert()
    return pygame.transform.scale(imagem, (LARGURA_TELA, ALTURA_TELA))


def desenhar_jogo(tela, fundo, clima, personagem, gerenciador_chao, pontos, powerups, multiplicador, vidas):
    tela.blit(fundo, (0, 0))
    clima.desenhar(tela)

    gerenciador_chao.desenhar(tela)
    personagem.desenhar(tela)

    texto_pontos = FONTE_PONTOS.render(f"Pontos: {pontos}", True, cores['verde-logo'])
    tela.blit(texto_pontos, (20, 20))
    desenhar_hud(tela, powerups, multiplicador, vidas)


def desenhar_gameover(tela, imagem_menu, mensagem_gameover):
    tela.fill((255, 0, 0))
    tela.blit(imagem_menu, (0, 0))

    rect = mensagem_gameover.get_rect(center=(LARGURA_TELA // 2, ALTURA_TELA // 2.5))
    tela.blit(mensagem_gameover, rect)

    botao_reiniciar.desenhar(tela)
    botao_menu.desenhar(tela)
    botao_sair_gameover.desenhar(tela)


