from game.configuracoes import FPS

ACERTOS_PARA_POWERUP = 3
SEGUNDOS_PULO_DUPLO = 10
SEGUNDOS_CAMERA_LENTA = 8

# duracao em frames; None = vale até ser usado
POWERUPS = {
    "escudo": {
        "nome": "Escudo",
        "descricao": "Absorve o próximo golpe de um obstáculo ou vilão",
        "duracao": None,
    },
    "pulo_duplo": {
        "nome": "Pulo duplo",
        "descricao": f"Permite um pulo extra no ar por {SEGUNDOS_PULO_DUPLO} segundos",
        "duracao": SEGUNDOS_PULO_DUPLO * FPS,
    },
    "camera_lenta": {
        "nome": "Câmera lenta",
        "descricao": f"O chão fica mais lento por {SEGUNDOS_CAMERA_LENTA} segundos",
        "duracao": SEGUNDOS_CAMERA_LENTA * FPS,
    },
}


class PowerUps:
    def __init__(self):
        self.resetar()

    def resetar(self):
        self.moedas = 0
        self.restante = {}

    def ganhar(self, moedas):
        self.moedas += moedas

    def ativo(self, chave):
        return chave in self.restante

    def ativar(self, chave):
        self.restante[chave] = POWERUPS[chave]["duracao"]

    def consumir(self, chave):
        self.restante.pop(chave, None)

    def atualizar(self):
        for chave in list(self.restante):
            if self.restante[chave] is None:
                continue
            self.restante[chave] -= 1
            if self.restante[chave] <= 0:
                del self.restante[chave]
