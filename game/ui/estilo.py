import pygame

from game.ui.fontes import esc

# madeira e papel, como as placas do mapa
COR_MADEIRA = (156, 100, 54)
COR_MADEIRA_ESCURA = (88, 52, 26)
COR_MADEIRA_CLARA = (205, 150, 88)
COR_VEIO = (140, 90, 48)
COR_PAPEL = (252, 240, 208)
COR_PAPEL_HOVER = (255, 250, 232)
COR_BORDA_PAPEL = (168, 118, 66)
COR_TINTA = (70, 42, 20)
COR_CREME = (255, 246, 220)
COR_DICA = (225, 200, 160)

COR_TITULO = (255, 225, 60)
COR_CERTA = (46, 160, 67)
COR_ERRADA = (200, 60, 60)
COR_ALERTA = (255, 200, 40)
COR_NEUTRA = (120, 108, 98)
COR_ERRO = (255, 70, 90)
COR_ERRO_TEXTO = (255, 160, 160)
COR_SUCESSO_TEXTO = (170, 240, 120)

# azul, roxo, laranja e rosa: uma cor para cada alternativa
CORES_ALTERNATIVAS = ((30, 136, 229), (123, 76, 196), (205, 98, 18), (219, 67, 140))


def clarear(cor, valor=35):
    return tuple(min(255, c + valor) for c in cor)


def escurecer(cor, fator=0.55):
    return tuple(int(c * fator) for c in cor)


def desenhar_placa(tela, rect, raio=esc(16), veios=True):
    """Painel de madeira com borda escura e sombra"""
    pygame.draw.rect(tela, COR_MADEIRA_ESCURA, rect.move(0, esc(8)), border_radius=raio)
    pygame.draw.rect(tela, COR_MADEIRA, rect, border_radius=raio)
    if veios:
        passo = esc(46)
        for y in range(rect.y + passo, rect.bottom - passo // 2, passo):
            pygame.draw.line(tela, COR_VEIO, (rect.x + esc(10), y), (rect.right - esc(10), y), 2)
    pygame.draw.rect(tela, COR_MADEIRA_ESCURA, rect, esc(6), border_radius=raio)
    pygame.draw.rect(tela, COR_MADEIRA_CLARA, rect.inflate(-esc(16), -esc(16)), 2, border_radius=raio)


def desenhar_papel(tela, rect, borda=COR_BORDA_PAPEL, fundo=COR_PAPEL, raio=esc(10)):
    pygame.draw.rect(tela, fundo, rect, border_radius=raio)
    pygame.draw.rect(tela, borda, rect, esc(3), border_radius=raio)


def desenhar_botao_colorido(tela, rect, cor, relevo=esc(5), raio=esc(12)):
    """Botão com a parte de baixo mais escura, dando o efeito de relevo."""
    pygame.draw.rect(tela, escurecer(cor), rect.move(0, relevo), border_radius=raio)
    pygame.draw.rect(tela, cor, rect, border_radius=raio)


def _contorno_degrau(rect, canto):
    x, y, w, h = rect
    return [(x + canto, y), (x + w - canto, y), (x + w - canto, y + canto), (x + w, y + canto),
            (x + w, y + h - canto), (x + w - canto, y + h - canto), (x + w - canto, y + h),
            (x + canto, y + h), (x + canto, y + h - canto), (x, y + h - canto),
            (x, y + canto), (x + canto, y + canto)]


def desenhar_bloco_pixel(tela, rect, fundo, borda, canto=esc(4), espessura=esc(4), sombra=esc(5)):
    """Bloco de pixel art"""
    if sombra:
        pygame.draw.polygon(tela, escurecer(borda, 0.45), _contorno_degrau(rect.move(0, sombra), canto))
    pygame.draw.polygon(tela, borda, _contorno_degrau(rect, canto))
    miolo = rect.inflate(-2 * espessura, -2 * espessura)
    pygame.draw.polygon(tela, fundo, _contorno_degrau(miolo, canto))
    pygame.draw.rect(tela, clarear(fundo, 40), (miolo.x + canto, miolo.y, miolo.width - 2 * canto, max(2, espessura // 2)))


# contorno, fundo, faixa de baixo, brilho: as mesmas cores dos botões em imagem
PALETAS = {
    "azul": ((16, 28, 92), (40, 100, 230), (30, 70, 190), (120, 170, 255)),
    "verde": ((18, 70, 30), (90, 205, 60), (40, 140, 35), (175, 240, 110)),
    "vermelho": ((90, 16, 24), (226, 62, 62), (180, 40, 48), (255, 140, 140)),
    "roxo": ((45, 22, 90), (135, 85, 215), (105, 60, 180), (195, 165, 255)),
    "dourado": ((92, 52, 10), (240, 170, 30), (200, 125, 15), (255, 225, 130)),
    "prata": ((52, 58, 76), (190, 198, 214), (150, 158, 176), (240, 244, 255)),
    "bronze": ((70, 36, 12), (205, 127, 50), (160, 95, 35), (240, 180, 110)),
    "marinho": ((10, 14, 36), (22, 32, 78), (16, 24, 60), (60, 80, 160)),
}


def desenhar_botao_pixel(tela, rect, paleta, unidade=esc(4)):
    contorno, fundo, faixa, brilho = paleta
    u = unidade
    pygame.draw.polygon(tela, contorno, _contorno_degrau(rect, u))
    interno = rect.inflate(-2 * u, -2 * u)
    corpo = pygame.Rect(interno.x, interno.y, interno.width, interno.height - 3 * u)
    pygame.draw.rect(tela, fundo, corpo)
    pygame.draw.rect(tela, brilho, (corpo.x + u, corpo.y, corpo.width - 2 * u, u))
    pygame.draw.rect(tela, brilho, (corpo.x, corpo.y + u, u, corpo.height - u))
    pygame.draw.rect(tela, faixa, (corpo.right - u, corpo.y + u, u, corpo.height - u))
    pygame.draw.rect(tela, contorno, (interno.x, corpo.bottom, interno.width, u))
    pygame.draw.rect(tela, faixa, (interno.x, corpo.bottom + u, interno.width, 2 * u))
    if rect.width > 12 * u:
        pygame.draw.rect(tela, (255, 255, 255), (rect.x + 4 * u, rect.y + 3 * u, 2 * u, u))
        pygame.draw.rect(tela, (255, 255, 255), (rect.x + 4 * u, rect.y + 4 * u, u, u))



