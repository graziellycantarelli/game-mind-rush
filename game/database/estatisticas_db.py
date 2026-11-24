from collections import defaultdict
from contextlib import closing

from game.database import db


def resumo(jogador_id):
    """Números da tela de estatísticas; as matérias juntam as perguntas do banco e os flashcards do jogador."""
    with closing(db._conectar()) as con:
        partidas, melhor, moedas = con.execute(
            "SELECT COUNT(*), COALESCE(MAX(CAST(pontuacao AS INTEGER)), 0), COALESCE(SUM(moedas), 0) "
            "FROM partidas WHERE jogador_id = ?", (jogador_id,)).fetchone()

        materias = defaultdict(lambda: [0, 0])
        respostas = con.execute(
            "SELECT p.modo, r.acertou, COUNT(*) FROM respostas r "
            "JOIN perguntas p ON p.id = r.pergunta_id "
            "WHERE r.jogador_id = ? GROUP BY p.modo, r.acertou", (jogador_id,))
        for modo, acertou, quantidade in respostas:
            materias[modo][0 if acertou else 1] += quantidade

        acertos, erros = con.execute(
            "SELECT COALESCE(SUM(acertos), 0), COALESCE(SUM(erros), 0) "
            "FROM flashcards WHERE jogador_id = ?", (jogador_id,)).fetchone()
        materias["flashcard"][0] += acertos
        materias["flashcard"][1] += erros

        # perguntas cuja resposta mais recente foi errada: são as que voltam para revisão
        revisar = con.execute(
            "SELECT COUNT(*) FROM respostas r WHERE r.jogador_id = ? AND r.acertou = 0 AND r.id = "
            "(SELECT MAX(id) FROM respostas WHERE jogador_id = r.jogador_id AND pergunta_id = r.pergunta_id)",
            (jogador_id,)).fetchone()[0]

    return {"partidas": partidas, "melhor": melhor, "moedas": moedas,
            "revisar": revisar, "materias": dict(materias)}
