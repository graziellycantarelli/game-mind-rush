"""Gera perguntas com IA para revisão manual e importa as aprovadas no banco.

python -m tools.gerar_perguntas gerar historia 20
(revise perguntas_geradas_historia.json e marque "aprovada": true nas corretas)
python -m tools.gerar_perguntas importar perguntas_geradas_historia.json

Precisa de: pip install anthropic, e da variável de ambiente ANTHROPIC_API_KEY.
"""

import json
import os
import re
import sys

from game.database import perguntas_db as db

MODELO = os.environ.get("MINDRUSH_MODELO", "claude-sonnet-5-5")

ASSUNTOS = {
    "computacao": "Computação (programação, estruturas de dados, redes, bancos de dados, sistemas operacionais)",
    "historia": "História do Brasil e geral, em nível de ensino médio e início de graduação",
    "medvet": "Medicina Veterinária (anatomia, fisiologia, doenças, clínica de pequenos e grandes animais)",
    "letras": "Letras (gramática, literatura brasileira e portuguesa, interpretação de texto)",
    "flashcard": "cultura geral escolar (ciências, geografia, matemática básica, artes)",
}


def montar_prompt(modo, quantidade, existentes):
    ja_existem = "\n".join(f"- {e}" for e in existentes) or "(nenhuma)"
    return f"""Crie {quantidade} perguntas de múltipla escolha em português do Brasil sobre: {ASSUNTOS[modo]}.

Regras:
- Cada pergunta tem exatamente 1 alternativa certa e 3 erradas, plausíveis mas inequivocamente erradas.
- Só inclua fatos que você tem certeza e que não dependam de opinião ou de data recente.
- Misture dificuldades: 1 (fácil), 2 (média), 3 (difícil).
- Enunciados curtos (até 160 caracteres) e alternativas curtas (até 60 caracteres).
- Não repita nem reformule estas perguntas que já existem:
{ja_existem}

Responda SOMENTE com um array JSON, sem texto antes ou depois, neste formato:
[{{"enunciado": "...", "certa": "...", "erradas": ["...", "...", "..."], "dificuldade": 1}}]"""


def extrair_json(texto):
    texto = re.sub(r"^```(?:json)?\s*|\s*```$", "", texto.strip())
    return json.loads(texto)


def para_tupla(item):
    erradas = item["erradas"]
    return (item["enunciado"], item["certa"], *erradas, item["dificuldade"])


def filtrar_validas(modo, itens, existentes):
    vistos = {e.strip().lower() for e in existentes}
    validas, descartes = [], []
    for item in itens:
        try:
            tupla = para_tupla(item)
            erro = db.validar(modo, tupla)
        except (KeyError, TypeError):
            erro = "formato inesperado"
        if not erro and tupla[0].strip().lower() in vistos:
            erro = "enunciado repetido"
        if erro:
            descartes.append(f"{erro}: {str(item)[:70]}")
            continue
        vistos.add(tupla[0].strip().lower())
        validas.append(item)
    return validas, descartes


def gerar(modo, quantidade):
    if modo not in ASSUNTOS:
        sys.exit(f"Modo inválido. Use um de: {', '.join(ASSUNTOS)}")
    try:
        import anthropic
    except ImportError:
        sys.exit("Instale a biblioteca primeiro: pip install anthropic")
    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("Defina a variável de ambiente ANTHROPIC_API_KEY.")

    db.criar_tabelas_perguntas()
    existentes = db.enunciados(modo)

    cliente = anthropic.Anthropic()
    resposta = cliente.messages.create(
        model=MODELO,
        max_tokens=8000,
        messages=[{"role": "user", "content": montar_prompt(modo, quantidade, existentes)}],
    )
    itens = extrair_json(resposta.content[0].text)
    validas, descartes = filtrar_validas(modo, itens, existentes)

    for item in validas:
        item["aprovada"] = False
    saida = f"perguntas_geradas_{modo}.json"
    with open(saida, "w", encoding="utf-8") as arq:
        json.dump({"modo": modo, "perguntas": validas}, arq, ensure_ascii=False, indent=2)

    print(f"{len(validas)} perguntas salvas em {saida} (todas com aprovada=false).")
    for d in descartes:
        print("  descartada ->", d)
    print("Agora revise o arquivo, marque aprovada=true nas corretas e rode o passo 'importar'.")


def importar(arquivo):
    with open(arquivo, encoding="utf-8") as arq:
        dados = json.load(arq)
    modo = dados["modo"]
    aprovadas = [para_tupla(p) for p in dados["perguntas"] if p.get("aprovada") is True]
    if not aprovadas:
        sys.exit("Nenhuma pergunta com aprovada=true neste arquivo.")

    db.criar_tabelas_perguntas()
    entraram = db.inserir_perguntas(modo, aprovadas, origem="gerada")
    print(f"{entraram} novas perguntas de '{modo}' no banco ({len(aprovadas) - entraram} já existiam).")


def main():
    args = sys.argv[1:]
    if len(args) == 3 and args[0] == "gerar" and args[2].isdigit():
        gerar(args[1], int(args[2]))
    elif len(args) == 2 and args[0] == "importar":
        importar(args[1])
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
