import os

import pygame

PASTA = "./audio"
EFEITOS = ("pulo", "moeda", "acerto", "erro", "powerup", "gameover")
VOLUME_EFEITOS = 0.6
VOLUME_MUSICA = 0.35


class Som:

    def __init__(self):
        self.efeitos_ligados = True
        self.musica_ligada = True
        self.musica_atual = None
        self.efeitos = {}
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
        except pygame.error:
            return
        for nome in EFEITOS:
            caminho = f"{PASTA}/{nome}.wav"
            if os.path.exists(caminho):
                self.efeitos[nome] = pygame.mixer.Sound(caminho)
                self.efeitos[nome].set_volume(VOLUME_EFEITOS)

    def tocar(self, nome):
        if self.efeitos_ligados and nome in self.efeitos:
            self.efeitos[nome].play()

    def musica(self, nome):
        if nome == self.musica_atual or not pygame.mixer.get_init():
            return
        self.musica_atual = nome
        caminho = f"{PASTA}/{nome}.ogg"
        if not os.path.exists(caminho):
            pygame.mixer.music.stop()
            return
        pygame.mixer.music.load(caminho)
        self._ajustar_volume_musica()
        pygame.mixer.music.play(-1)

    def _ajustar_volume_musica(self):
        if pygame.mixer.get_init():
            pygame.mixer.music.set_volume(VOLUME_MUSICA if self.musica_ligada else 0)

    def alternar_efeitos(self):
        self.efeitos_ligados = not self.efeitos_ligados

    def alternar_musica(self):
        self.musica_ligada = not self.musica_ligada
        self._ajustar_volume_musica()

    def alternar_tudo(self):
        ligar = not (self.efeitos_ligados and self.musica_ligada)
        self.efeitos_ligados = self.musica_ligada = ligar
        self._ajustar_volume_musica()

