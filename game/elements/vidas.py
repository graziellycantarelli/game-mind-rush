class Vidas:
    MAXIMO = 3
    ACERTOS_PARA_CURAR = 5

    def __init__(self):
        self.resetar()

    def resetar(self):
        self.atual = Vidas.MAXIMO
        self.acertos = 0

    def errar(self):
        self.atual = max(0, self.atual - 1)

    def acertar(self):
        self.acertos += 1
        if self.acertos % Vidas.ACERTOS_PARA_CURAR == 0:
            self.atual = min(Vidas.MAXIMO, self.atual + 1)
