import random
from contextlib import contextmanager

from game.database import db as _db

MODOS = ("computacao", "historia", "medvet", "letras", "flashcard")

# chance de sair uma pergunta de revisão (já errada) quando ainda há perguntas novas
CHANCE_REVISAO = 0.3

# perguntas já vistas por visitantes (sem conta) enquanto o jogo estiver aberto
_vistas_visitante = set()


def _conectar():
    con = _db._conectar()
    con.execute("PRAGMA foreign_keys = ON")
    return con


@contextmanager
def _sessao():
    con = _conectar()
    try:
        with con:
            yield con
    finally:
        con.close()


def criar_tabelas_perguntas():
    with _sessao() as con:
        con.executescript("""
            CREATE TABLE IF NOT EXISTS perguntas (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                modo        TEXT NOT NULL,
                enunciado   TEXT NOT NULL,
                certa       TEXT NOT NULL,
                errada1     TEXT NOT NULL,
                errada2     TEXT NOT NULL,
                errada3     TEXT NOT NULL,
                dificuldade INTEGER NOT NULL DEFAULT 1 CHECK (dificuldade BETWEEN 1 AND 3),
                origem      TEXT NOT NULL DEFAULT 'inicial',
                UNIQUE (modo, enunciado)
            );
            CREATE TABLE IF NOT EXISTS respostas (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                jogador_id  INTEGER NOT NULL,
                pergunta_id INTEGER NOT NULL REFERENCES perguntas(id) ON DELETE CASCADE,
                acertou     INTEGER NOT NULL,
                data        TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS idx_respostas_jogador
                ON respostas (jogador_id, pergunta_id);
        """)


def validar(modo, pergunta):
    if modo not in MODOS:
        return f"modo desconhecido: {modo}"
    if len(pergunta) != 6:
        return "formato esperado: (enunciado, certa, errada, errada, errada, dificuldade)"
    enunciado, *alternativas, dificuldade = pergunta
    if not all(isinstance(t, str) and t.strip() for t in [enunciado, *alternativas]):
        return "texto vazio"
    if len({a.strip().lower() for a in alternativas}) != 4:
        return "alternativas repetidas"
    if dificuldade not in (1, 2, 3):
        return "dificuldade deve ser 1, 2 ou 3"
    return None


def inserir_perguntas(modo, perguntas, origem="inicial"):
    for p in perguntas:
        erro = validar(modo, p)
        if erro:
            raise ValueError(f"{erro}: {p[0] if p else p!r}")

    entraram = 0
    with _sessao() as con:
        for enunciado, certa, e1, e2, e3, dificuldade in perguntas:
            cursor = con.execute(
                "INSERT OR IGNORE INTO perguntas "
                "(modo, enunciado, certa, errada1, errada2, errada3, dificuldade, origem) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (modo, enunciado.strip(), certa.strip(), e1.strip(), e2.strip(), e3.strip(),
                 dificuldade, origem))
            entraram += cursor.rowcount
    return entraram


def semear_iniciais():
    from game.database.perguntas_iniciais import BANCO
    return sum(inserir_perguntas(modo, lista) for modo, lista in BANCO.items())


def enunciados(modo):
    with _sessao() as con:
        return [l[0] for l in con.execute("SELECT enunciado FROM perguntas WHERE modo = ?", (modo,))]


def _escolher(candidatas, jogador_id, vezes, ultima):
    if jogador_id is None:
        novas = [l for l in candidatas if l[0] not in _vistas_visitante]
        revisao = []
    else:
        novas = [l for l in candidatas if l[0] not in vezes]
        revisao = [l for l in candidatas if ultima.get(l[0]) == 0]

    if novas and revisao:
        return random.choice(revisao if random.random() < CHANCE_REVISAO else novas)
    if novas:
        return random.choice(novas)
    if revisao:
        return random.choice(revisao)
    pesos = [1.0 / (1 + vezes.get(l[0], 0)) for l in candidatas]
    return random.choices(candidatas, weights=pesos)[0]


def sortear(modo, feitas, jogador_id=None, dificuldade_max=3):
    """feitas: enunciados já perguntados na partida. jogador_id None = visitante.
    dificuldade_max: ignorado se não sobrar nenhuma pergunta dentro do limite."""
    with _sessao() as con:
        linhas = con.execute(
            "SELECT id, enunciado, certa, errada1, errada2, errada3, dificuldade "
            "FROM perguntas WHERE modo = ?", (modo,)).fetchall()
        vezes, ultima = {}, {}
        if jogador_id is not None:
            historico = con.execute(
                "SELECT pergunta_id, acertou FROM respostas WHERE jogador_id = ? ORDER BY id",
                (jogador_id,))
            for pid, acertou in historico:
                vezes[pid] = vezes.get(pid, 0) + 1
                ultima[pid] = acertou

    if not linhas:
        raise ValueError(f"não há perguntas do modo '{modo}' no banco")

    candidatas = [l for l in linhas if l[1] not in feitas] or linhas
    candidatas = [l for l in candidatas if l[6] <= dificuldade_max] or candidatas

    if jogador_id is None and all(l[0] in _vistas_visitante for l in linhas):
        _vistas_visitante.difference_update(l[0] for l in linhas)

    pid, enunciado, certa, *erradas, _ = _escolher(candidatas, jogador_id, vezes, ultima)

    alternativas = [certa, *erradas]
    random.shuffle(alternativas)
    return {
        "id": pid,
        "modo": modo,
        "enunciado": enunciado,
        "alternativas": alternativas,
        "correta": alternativas.index(certa),
        "certa": certa,
    }


def registrar_resposta(jogador_id, pergunta_id, acertou):
    if jogador_id is None:
        _vistas_visitante.add(pergunta_id)
        return
    with _sessao() as con:
        con.execute(
            "INSERT INTO respostas (jogador_id, pergunta_id, acertou) VALUES (?, ?, ?)",
            (jogador_id, pergunta_id, int(acertou)))


def apagar_respostas_do_jogador(jogador_id):
    with _sessao() as con:
        con.execute("DELETE FROM respostas WHERE jogador_id = ?", (jogador_id,))
