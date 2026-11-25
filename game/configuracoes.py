import pygame

pygame.init()
pygame.font.init()

# Configurações de tela
FULLSCREEN = True

info_tela = pygame.display.Info()
LARGURA_TELA = info_tela.current_w
ALTURA_TELA = info_tela.current_h

# título do jogo
TITULO_JOGO = "Mind Rush"

# fontes
FONTE_TITULO = pygame.font.SysFont('arial', 60)
FONTE_MENSAGEM = pygame.font.Font('./fontes/aseprite.ttf', 50)
FONTE_PONTOS = pygame.font.Font('./fontes/aseprite.ttf', 60)

# taxa de quadros
FPS = 60

# caminho da imagem do menu
CAMINHO_MENU = './img/fundos/MENU.png'
imagem_menu = pygame.image.load(CAMINHO_MENU)
imagem_menu = pygame.transform.scale(imagem_menu, (LARGURA_TELA, ALTURA_TELA))

# caminho da imagem de fundo do jogo
CAMINHO_BG_JOGO = './img/fundos/bg_jogo.png'
imagem_bg_jogo = pygame.image.load(CAMINHO_BG_JOGO)
imagem_bg_jogo = pygame.transform.scale(imagem_bg_jogo, (LARGURA_TELA, ALTURA_TELA))

# caminho da imagem de fundo do cadastro
CAMINHO_BG_CADASTRO = './img/fundos/bg_cadastro.png'
imagem_bg_cadastro = pygame.image.load(CAMINHO_BG_CADASTRO)
imagem_bg_cadastro = pygame.transform.scale(imagem_bg_cadastro, (LARGURA_TELA, ALTURA_TELA))

CAMINHO_IMAGEM_GAMEOVER = './img/fundos/GAMEOVER.png'
imagem_gameover = pygame.image.load(CAMINHO_IMAGEM_GAMEOVER)
imagem_gameover = pygame.transform.scale(imagem_gameover, (LARGURA_TELA, ALTURA_TELA))

CAMINHO_MENSAGEM_GAMEOVER = './img/mensagem/MORREUMR.png'
mensagem_gameover = pygame.image.load(CAMINHO_MENSAGEM_GAMEOVER)
largura_mensagem = int(LARGURA_TELA * 0.5)
mensagem_gameover = pygame.transform.smoothscale(
    mensagem_gameover, (largura_mensagem, round(mensagem_gameover.get_height() * largura_mensagem / mensagem_gameover.get_width())))

