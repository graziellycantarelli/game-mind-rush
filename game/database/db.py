import sqlite3
import hashlib
import hmac
import os
from contextlib import closing

CAMINHO_DB = './game/database/banco.db'
ITERACOES_HASH = 200_000


def _conectar():
    return sqlite3.connect(CAMINHO_DB)


def _gerar_hash(senha, salt):
    # PBKDF2 com salt: a senha nunca é guardada em texto puro
    return hashlib.pbkdf2_hmac('sha256', senha.encode('utf-8'), salt, ITERACOES_HASH).hex()


def criar_tabelas():
    with closing(_conectar()) as conn, conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS jogadores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT NOT NULL UNIQUE COLLATE NOCASE,
            email TEXT NOT NULL UNIQUE,
            senha_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            data_nascimento TEXT NOT NULL,
            tutorial_visto INTEGER NOT NULL DEFAULT 0
        )
        """)

        conn.execute("""
        CREATE TABLE IF NOT EXISTS partidas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pontuacao INTEGER NOT NULL,
            jogador_id INTEGER REFERENCES jogadores(id),
            moedas INTEGER NOT NULL DEFAULT 0
        )
        """)

        # migração: bancos antigos não têm as colunas jogador_id e moedas
        colunas = [c[1] for c in conn.execute("PRAGMA table_info(partidas)").fetchall()]
        if "jogador_id" not in colunas:
            conn.execute("ALTER TABLE partidas ADD COLUMN jogador_id INTEGER")
        colunas_jogadores = [c[1] for c in conn.execute("PRAGMA table_info(jogadores)").fetchall()]
        if "tutorial_visto" not in colunas_jogadores:
            conn.execute("ALTER TABLE jogadores ADD COLUMN tutorial_visto INTEGER NOT NULL DEFAULT 0")
        if "moedas" not in colunas:
            conn.execute("ALTER TABLE partidas ADD COLUMN moedas INTEGER NOT NULL DEFAULT 0")


# jogadores

def usuario_existe(usuario, ignorar_id=0):
    """ignorar_id evita que o próprio jogador conte como 'já existe' ao trocar de nome."""
    with closing(_conectar()) as conn:
        linha = conn.execute(
            "SELECT 1 FROM jogadores WHERE usuario = ? COLLATE NOCASE AND id != ?",
            (usuario, ignorar_id)
        ).fetchone()
    return linha is not None


def email_existe(email):
    with closing(_conectar()) as conn:
        linha = conn.execute(
            "SELECT 1 FROM jogadores WHERE email = ?", (email.lower(),)
        ).fetchone()
    return linha is not None


def inserir_jogador(usuario, email, senha, data_nascimento_iso):
    salt = os.urandom(16)
    senha_hash = _gerar_hash(senha, salt)

    with closing(_conectar()) as conn, conn:
        cursor = conn.execute(
            "INSERT INTO jogadores (usuario, email, senha_hash, salt, data_nascimento) "
            "VALUES (?, ?, ?, ?, ?)",
            (usuario, email.lower(), senha_hash, salt.hex(), data_nascimento_iso)
        )
        return cursor.lastrowid


def autenticar(usuario, senha):
    """Retorna {'id', 'usuario'} se usuário e senha batem, senão None."""
    with closing(_conectar()) as conn:
        linha = conn.execute(
            "SELECT id, usuario, senha_hash, salt FROM jogadores "
            "WHERE usuario = ? COLLATE NOCASE", (usuario,)
        ).fetchone()

    if linha is None:
        return None

    jogador_id, nome, senha_hash, salt_hex = linha
    hash_calculado = _gerar_hash(senha, bytes.fromhex(salt_hex))

    if hmac.compare_digest(hash_calculado, senha_hash):
        return {"id": jogador_id, "usuario": nome}
    return None


def atualizar_senha(jogador_id, nova_senha):
    salt = os.urandom(16)

    with closing(_conectar()) as conn, conn:
        conn.execute(
            "UPDATE jogadores SET senha_hash = ?, salt = ? WHERE id = ?",
            (_gerar_hash(nova_senha, salt), salt.hex(), jogador_id)
        )


def atualizar_usuario(jogador_id, novo_usuario):
    with closing(_conectar()) as conn, conn:
        conn.execute(
            "UPDATE jogadores SET usuario = ? WHERE id = ?",
            (novo_usuario, jogador_id)
        )


def tutorial_visto(jogador_id):
    with closing(_conectar()) as conn:
        linha = conn.execute("SELECT tutorial_visto FROM jogadores WHERE id = ?", (jogador_id,)).fetchone()
    return bool(linha and linha[0])


def marcar_tutorial_visto(jogador_id):
    with closing(_conectar()) as conn, conn:
        conn.execute("UPDATE jogadores SET tutorial_visto = 1 WHERE id = ?", (jogador_id,))


def apagar_jogador(jogador_id):
    with closing(_conectar()) as conn, conn:
        conn.execute("DELETE FROM respostas WHERE jogador_id = ?", (jogador_id,))
        conn.execute("DELETE FROM partidas WHERE jogador_id = ?", (jogador_id,))
        conn.execute("DELETE FROM jogadores WHERE id = ?", (jogador_id,))


# pontuação

def salvar_pontuacao(jogador_id, pontuacao, moedas=0):
    with closing(_conectar()) as conn, conn:
        # Os ? garantem que o sqlite3 trata o valor como dado, nunca como código SQL
        conn.execute(
            "INSERT INTO partidas (pontuacao, jogador_id, moedas) VALUES (?, ?, ?)",
            (pontuacao, jogador_id, moedas)
        )


def get_top5_pontuacao(jogador_id):
    """Top 5 pontuações apenas do jogador informado."""
    with closing(_conectar()) as conn:
        linhas = conn.execute(
            "SELECT pontuacao FROM partidas WHERE jogador_id = ? "
            "ORDER BY CAST(pontuacao AS INTEGER) DESC LIMIT 5",
            (jogador_id,)
        ).fetchall()

    return [linha[0] for linha in linhas]
