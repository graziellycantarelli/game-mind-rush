import unicodedata

PONTUACAO = " .,;:!?"


def normalizar(texto):
    decomposto = unicodedata.normalize("NFD", texto)
    sem_acento = "".join(c for c in decomposto if not unicodedata.combining(c))
    return " ".join(sem_acento.lower().split()).strip(PONTUACAO)


def respostas_iguais(digitada, correta):
    return normalizar(digitada) == normalizar(correta)
