from contextlib import closing

from game.database import db


def criar_tabelas_loja():
    with closing(db._conectar()) as con, con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS compras (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                jogador_id INTEGER NOT NULL,
                item       TEXT NOT NULL,
                tipo       TEXT NOT NULL,
                preco      INTEGER NOT NULL,
                equipado   INTEGER NOT NULL DEFAULT 0,
                UNIQUE (jogador_id, item)
            )
        """)


def _saldo(con, jogador_id):
    ganho = con.execute("SELECT COALESCE(SUM(moedas), 0) FROM partidas WHERE jogador_id = ?",
                        (jogador_id,)).fetchone()[0]
    gasto = con.execute("SELECT COALESCE(SUM(preco), 0) FROM compras WHERE jogador_id = ?",
                        (jogador_id,)).fetchone()[0]
    return ganho - gasto


def saldo(jogador_id):
    with closing(db._conectar()) as con:
        return _saldo(con, jogador_id)


def comprados(jogador_id):
    with closing(db._conectar()) as con:
        linhas = con.execute("SELECT item FROM compras WHERE jogador_id = ?", (jogador_id,)).fetchall()
    return {linha[0] for linha in linhas}


def equipados(jogador_id):
    """{tipo: item} do que o jogador está usando."""
    with closing(db._conectar()) as con:
        linhas = con.execute("SELECT tipo, item FROM compras WHERE jogador_id = ? AND equipado = 1",
                            (jogador_id,)).fetchall()
    return dict(linhas)


def comprar(jogador_id, item, tipo, preco):
    """True se a compra foi feita: precisa de saldo e de o item ainda não ser do jogador."""
    with closing(db._conectar()) as con, con:
        if _saldo(con, jogador_id) < preco:
            return False
        cursor = con.execute(
            "INSERT OR IGNORE INTO compras (jogador_id, item, tipo, preco) VALUES (?, ?, ?, ?)",
            (jogador_id, item, tipo, preco))
        return cursor.rowcount == 1


def equipar(jogador_id, tipo, item):
    """item None volta ao visual padrão do modo."""
    with closing(db._conectar()) as con, con:
        con.execute("UPDATE compras SET equipado = 0 WHERE jogador_id = ? AND tipo = ?", (jogador_id, tipo))
        if item:
            con.execute("UPDATE compras SET equipado = 1 WHERE jogador_id = ? AND item = ?", (jogador_id, item))


def apagar_do_jogador(jogador_id):
    with closing(db._conectar()) as con, con:
        con.execute("DELETE FROM compras WHERE jogador_id = ?", (jogador_id,))
