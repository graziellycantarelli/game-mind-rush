import random
from contextlib import contextmanager

from game.database import db as _db


@contextmanager
def _sessao():
    con = _db._conectar()
    try:
        with con:
            yield con
    finally:
        con.close()


def criar_tabelas_flashcards():
    with _sessao() as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS flashcards (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                jogador_id INTEGER NOT NULL,
                pergunta   TEXT NOT NULL COLLATE NOCASE,
                resposta   TEXT NOT NULL,
                acertos    INTEGER NOT NULL DEFAULT 0,
                erros      INTEGER NOT NULL DEFAULT 0,
                UNIQUE (jogador_id, pergunta)
            )
        """)


def listar(jogador_id):
    with _sessao() as con:
        linhas = con.execute(
            "SELECT id, pergunta, resposta FROM flashcards WHERE jogador_id = ? ORDER BY id DESC",
            (jogador_id,)).fetchall()
    return [{"id": i, "pergunta": p, "resposta": r} for i, p, r in linhas]


def adicionar(jogador_id, pergunta, resposta):
    pergunta, resposta = pergunta.strip(), resposta.strip()
    if not pergunta or not resposta:
        return False
    with _sessao() as con:
        cursor = con.execute(
            "INSERT OR IGNORE INTO flashcards (jogador_id, pergunta, resposta) VALUES (?, ?, ?)",
            (jogador_id, pergunta, resposta))
        return cursor.rowcount == 1


def apagar(jogador_id, carta_id):
    # jogador_id na condição: ninguém apaga o card de outro
    with _sessao() as con:
        con.execute("DELETE FROM flashcards WHERE id = ? AND jogador_id = ?", (carta_id, jogador_id))


def apagar_todos_do_jogador(jogador_id):
    with _sessao() as con:
        con.execute("DELETE FROM flashcards WHERE jogador_id = ?", (jogador_id,))


def sortear(jogador_id, feitas):
    """Devolve um card do jogador."""
    with _sessao() as con:
        linhas = con.execute(
            "SELECT id, pergunta, resposta, acertos, erros FROM flashcards WHERE jogador_id = ?",
            (jogador_id,)).fetchall()
    if not linhas:
        return None

    candidatas = [l for l in linhas if l[1] not in feitas] or linhas
    novas = [l for l in candidatas if l[3] + l[4] == 0]
    if novas:
        escolhida = random.choice(novas)
    else:
        pesos = [(l[4] + 1) / (l[3] + l[4] + 2) for l in candidatas]
        escolhida = random.choices(candidatas, weights=pesos)[0]

    carta_id, pergunta, resposta, _, _ = escolhida
    return {"id": carta_id, "enunciado": pergunta, "resposta": resposta}


def registrar(carta_id, acertou):
    coluna = "acertos" if acertou else "erros"
    with _sessao() as con:
        con.execute(f"UPDATE flashcards SET {coluna} = {coluna} + 1 WHERE id = ?", (carta_id,))
