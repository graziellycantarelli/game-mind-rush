import math

import pygame

from game.configuracoes import LARGURA_TELA, ALTURA_TELA, FONTE_MENSAGEM, FONTE_PONTOS, FPS
from game.elements.powerups import POWERUPS
from game.ui.conta import FontePixel
from game.util.cores import cores

ESCALA = ALTURA_TELA / 1080
MARGEM = 20
ESPACO = int(12 * ESCALA)
PREENCHIMENTO = int(12 * ESCALA)
LARGURA_SLOT = int(290 * ESCALA)
RAIO_MOEDA = int(22 * ESCALA)

COR_PAINEL = (20, 30, 60, 210)
COR_MOEDA = (255, 200, 40)
COR_BORDA_MOEDA = (190, 130, 20)
COR_CORACAO = (230, 50, 60)
COR_CORACAO_VAZIO = (70, 40, 50)
LADO_CORACAO = int(56 * ESCALA)
BORDA_CORACAO = max(2, int(4 * ESCALA))

FONTE_SLOT = FontePixel(30)
FONTE_DETALHE = FontePixel(26)
ALTURA_SLOT = 2 * PREENCHIMENTO + FONTE_SLOT.get_linesize() + FONTE_DETALHE.get_linesize()


def _desenhar_moedas(tela, moedas):
    centro = (MARGEM + RAIO_MOEDA, MARGEM + FONTE_PONTOS.get_linesize() + RAIO_MOEDA)
    pygame.draw.circle(tela, COR_MOEDA, centro, RAIO_MOEDA)
    pygame.draw.circle(tela, COR_BORDA_MOEDA, centro, RAIO_MOEDA, 4)
    texto = FONTE_MENSAGEM.render(f"x {moedas}", True, COR_MOEDA)
    tela.blit(texto, texto.get_rect(midleft=(centro[0] + RAIO_MOEDA + ESPACO, centro[1])))


def _desenhar_ativo(tela, powerups, chave, powerup, x):
    rect = pygame.Rect(x, MARGEM, LARGURA_SLOT, ALTURA_SLOT)
    cor = cores['verde-logo']

    fundo = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(fundo, COR_PAINEL, fundo.get_rect(), border_radius=10)
    tela.blit(fundo, rect)
    pygame.draw.rect(tela, cor, rect, 3, border_radius=10)

    detalhe = "ativo" if powerup["duracao"] is None else f"{math.ceil(powerups.restante[chave] / FPS)}s"
    tela.blit(FONTE_SLOT.render(powerup["nome"], True, cor), (rect.x + PREENCHIMENTO, rect.y + PREENCHIMENTO))
    tela.blit(FONTE_DETALHE.render(detalhe, True, cor),
            (rect.x + PREENCHIMENTO, rect.y + PREENCHIMENTO + FONTE_SLOT.get_linesize()))


def _desenhar_combo(tela, multiplicador):
    y = MARGEM + FONTE_PONTOS.get_linesize() + 2 * RAIO_MOEDA + ESPACO
    tela.blit(FONTE_MENSAGEM.render(f"Combo x{multiplicador}", True, cores['verde-logo']), (MARGEM, y))


def _coracao(tela, centro, lado, cor):
    r = lado // 4
    x, y = centro
    pygame.draw.circle(tela, cor, (x - r, y - r // 2), r)
    pygame.draw.circle(tela, cor, (x + r, y - r // 2), r)
    pygame.draw.polygon(tela, cor, [(x - 2 * r, y - r // 2), (x + 2 * r, y - r // 2), (x, y + 2 * r)])


def _desenhar_vidas(tela, vidas):
    espaco = int(12 * ESCALA)
    total = vidas.MAXIMO * LADO_CORACAO + (vidas.MAXIMO - 1) * espaco
    x = (LARGURA_TELA - total) // 2 + LADO_CORACAO // 2
    y = MARGEM + LADO_CORACAO // 2 + BORDA_CORACAO
    for i in range(vidas.MAXIMO):
        centro = (x + i * (LADO_CORACAO + espaco), y)
        _coracao(tela, centro, LADO_CORACAO + 2 * BORDA_CORACAO, cores['branco'])
        _coracao(tela, centro, LADO_CORACAO, COR_CORACAO if i < vidas.atual else COR_CORACAO_VAZIO)


def desenhar_hud(tela, powerups, multiplicador, vidas):
    _desenhar_vidas(tela, vidas)
    _desenhar_moedas(tela, powerups.moedas)
    if multiplicador >= 2:
        _desenhar_combo(tela, multiplicador)

    ativos = [(chave, powerup) for chave, powerup in POWERUPS.items() if powerups.ativo(chave)]
    x = LARGURA_TELA - MARGEM - len(ativos) * LARGURA_SLOT - max(0, len(ativos) - 1) * ESPACO
    for chave, powerup in ativos:
        _desenhar_ativo(tela, powerups, chave, powerup, x)
        x += LARGURA_SLOT + ESPACO
