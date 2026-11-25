import os

PASTA = "./img/skins"


ITENS = [
    {"id": "flashcard_1", "modo": "flashcard", "nome": "Estudante Raro", "preco": 50},
    {"id": "flashcard_2", "modo": "flashcard", "nome": "Estudante Lendário", "preco": 100},
    {"id": "computacao_1", "modo": "computacao", "nome": "Hacker", "preco": 50},
    {"id": "computacao_2", "modo": "computacao", "nome": "Robô", "preco": 100},
    {"id": "historia_1", "modo": "historia", "nome": "Explorador", "preco": 50},
    {"id": "historia_2", "modo": "historia", "nome": "Faraó", "preco": 100},
    {"id": "medvet_1", "modo": "medvet", "nome": "Veterinário", "preco": 50},
    {"id": "medvet_2", "modo": "medvet", "nome": "Doutor Pet", "preco": 100},
    {"id": "letras_1", "modo": "letras", "nome": "Poeta", "preco": 50},
    {"id": "letras_2", "modo": "letras", "nome": "Escritor", "preco": 100},
]


def _item(item_id):
    return next((i for i in ITENS if i["id"] == item_id), None)


def _pasta(item):
    return f"{PASTA}/{item['modo']}"


def _numero(item):
    return item["id"].rsplit("_", 1)[1]


def _frames(item):
    return [f"{_pasta(item)}/skin{_numero(item)}_{i}.png" for i in (1, 2, 3)]


def _tem_frames(item):
    return all(os.path.exists(c) for c in _frames(item))


def disponiveis():
    return [i for i in ITENS if _tem_frames(i)]


def personagem(item_id):
    """Quadros do personagem da skin, ou None se ela não existe mais."""
    item = _item(item_id)
    return _frames(item) if item and _tem_frames(item) else None


def fundo(item_id):
    """Cenário da skin, ou None se ela não tem um."""
    item = _item(item_id)
    caminho = f"{_pasta(item)}/fundo_skin{_numero(item)}.png" if item else None
    return caminho if caminho and os.path.exists(caminho) else None

