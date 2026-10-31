"""Gera um rascunho de post de LinkedIn sobre inovação usando a API do Claude.

Saída: escreve o texto do post em `rascunho.md` (ou no caminho passado como
1º argumento). Variáveis de ambiente:
  ANTHROPIC_API_KEY   chave da API da Anthropic (obrigatória)
  POSTS_ANTERIORES    lista (uma por linha) de títulos já usados, para evitar repetição
  TEMA_EXTRA          (opcional) direcionamento específico para este post
"""

import datetime
import os
import pathlib
import re
import sys

import anthropic

MODELO = "claude-opus-5-5"
PASTA = pathlib.Path(__file__).parent
INICIO, FIM = "<<<POST>>>", "<<<FIM>>>"


def montar_prompt() -> str:
    perfil = (PASTA / "perfil.md").read_text(encoding="utf-8")
    hoje = datetime.date.today().strftime("%d/%m/%Y")
    anteriores = os.environ.get("POSTS_ANTERIORES", "").strip() or "(nenhum ainda)"
    extra = os.environ.get("TEMA_EXTRA", "").strip()

    return f"""Você é ghostwriter de LinkedIn. Hoje é {hoje}.

Escreva UM post de LinkedIn em português do Brasil seguindo este perfil editorial:

{perfil}

Antes de escrever, pesquise na web uma notícia, tendência ou caso real e recente
(últimas semanas) sobre inovação que renda uma boa reflexão. Use apenas fontes
confiáveis e não invente números.

Assuntos dos posts anteriores (NÃO repita estes ângulos):
{anteriores}
{f"Direcionamento para este post: {extra}" if extra else ""}

Responda exatamente neste formato:
TITULO: <resumo do assunto em até 8 palavras>
FONTE: <URL principal que você usou>
{INICIO}
<texto final do post, pronto para publicar, sem markdown (sem **negrito** nem # títulos)>
{FIM}"""


def gerar() -> str:
    client = anthropic.Anthropic()
    messages = [{"role": "user", "content": montar_prompt()}]
    tools = [{"type": "web_search_20260209", "name": "web_search", "max_uses": 5}]

    # pause_turn: a busca na web pode pausar o turno; basta reenviar para continuar.
    for _ in range(5):
        response = client.beta.messages.create(
            model=MODELO,
            max_tokens=16000,
            thinking={"type": "adaptive"},
            output_config={"effort": "high"},
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
            tools=tools,
            messages=messages,
        )
        if response.stop_reason != "pause_turn":
            break
        messages = messages + [{"role": "assistant", "content": response.content}]

    if response.stop_reason == "refusal":
        sys.exit(f"O modelo recusou o pedido: {response.stop_details}")

    texto = "".join(b.text for b in response.content if b.type == "text")
    if INICIO not in texto or FIM not in texto:
        sys.exit(f"Resposta fora do formato esperado:\n{texto}")
    return texto


def main() -> None:
    texto = gerar()
    titulo = re.search(r"TITULO:\s*(.+)", texto)
    fonte = re.search(r"FONTE:\s*(\S+)", texto)
    post = texto.split(INICIO, 1)[1].split(FIM, 1)[0].strip()

    saida = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "rascunho.md")
    saida.write_text(post + "\n", encoding="utf-8")
    pathlib.Path(str(saida) + ".titulo").write_text(
        (titulo.group(1).strip() if titulo else "Post sobre inovação"), encoding="utf-8"
    )
    pathlib.Path(str(saida) + ".fonte").write_text(
        (fonte.group(1).strip() if fonte else ""), encoding="utf-8"
    )
    print(post)


if __name__ == "__main__":
    main()
