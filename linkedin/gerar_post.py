"""Gera um rascunho de post de LinkedIn sobre inovação usando a API do Claude.

Saída: escreve o texto do post em `rascunho.md` (ou no caminho passado como
1º argumento). Variáveis de ambiente:
  ANTHROPIC_API_KEY   chave da API da Anthropic (obrigatória)
  POSTS_ANTERIORES    lista (uma por linha) de títulos já usados, para evitar repetição
  TEMA_EXTRA          (opcional) direcionamento específico para este post
  EVENTOS             (opcional) descrições das fotos da semana, enviadas pelo Atalho do iPhone
Também lê linkedin/contexto/ideias.md (ideias anotadas nas conversas).
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


def ler_ideias() -> str:
    arquivo = PASTA / "contexto" / "ideias.md"
    if not arquivo.exists():
        return ""
    conteudo = re.sub(r"<!--.*?-->", "", arquivo.read_text(encoding="utf-8"), flags=re.S)
    linhas = [
        l.strip() for l in conteudo.splitlines()
        if l.strip().startswith("- ") and "[usado]" not in l
    ]
    return "\n".join(linhas[-20:])


def montar_prompt() -> str:
    perfil = (PASTA / "perfil.md").read_text(encoding="utf-8")
    hoje = datetime.date.today().strftime("%d/%m/%Y")
    anteriores = os.environ.get("POSTS_ANTERIORES", "").strip() or "(nenhum ainda)"
    extra = os.environ.get("TEMA_EXTRA", "").strip()
    fotos = os.environ.get("EVENTOS", "").strip() or "(nenhuma foto enviada esta semana)"
    ideias = ler_ideias() or "(nenhuma ideia anotada)"

    return f"""Você é ghostwriter de LinkedIn. Hoje é {hoje}.

Escreva UM post de LinkedIn em português do Brasil seguindo este perfil editorial:

{perfil}

## Escolha do assunto — siga esta ordem de prioridade

1. EVENTO NAS FOTOS. Abaixo estão descrições (data, local, conteúdo) das fotos
   tiradas pela autora nos últimos 7 dias. Avalie se alguma indica participação
   em um evento profissional (congresso, palestra, workshop, feira, meetup,
   hackathon, curso, visita técnica, premiação — sinais: palco, plateia, crachá,
   slides, estandes, banners). Fotos pessoais (família, comida, lazer, documentos)
   devem ser ignoradas e nunca mencionadas. Se houver evento, o post é sobre essa
   experiência, em primeira pessoa. Use só o que as fotos mostram; o que não
   souber (nome do evento, palestrante, aprendizado específico) deixe como
   marcador entre colchetes, ex.: [nome do evento], para a autora completar.
   Pesquise na web o tema do evento para enriquecer o post com contexto atual.

2. IDEIAS DAS CONVERSAS. Se não houver evento, escolha a ideia mais promissora
   da lista abaixo (que ainda não tenha virado post) e desenvolva-a, buscando na
   web uma novidade recente que a conecte com tecnologia e inovação.

3. NOVIDADES. Se não houver nada aproveitável acima, pesquise na web as últimas
   atualizações de tecnologia e inovação (últimas 1–2 semanas) e escolha a que
   renda a melhor reflexão para o público do perfil.

Use apenas fontes confiáveis e não invente números, nomes ou fatos.

### Descrições das fotos da semana
{fotos}

### Ideias anotadas nas conversas
{ideias}

### Assuntos dos posts anteriores (NÃO repita estes ângulos)
{anteriores}
{f"{chr(10)}### Direcionamento extra para este post{chr(10)}{extra}" if extra else ""}

Responda exatamente neste formato:
ORIGEM: <evento | ideia | novidade>
TITULO: <resumo do assunto em até 8 palavras>
FONTE: <URL principal que você usou, ou "fotos" se não houver>
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
    origem = re.search(r"ORIGEM:\s*(\S+)", texto)
    post = texto.split(INICIO, 1)[1].split(FIM, 1)[0].strip()

    saida = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "rascunho.md")
    saida.write_text(post + "\n", encoding="utf-8")
    pathlib.Path(str(saida) + ".titulo").write_text(
        (titulo.group(1).strip() if titulo else "Post sobre inovação"), encoding="utf-8"
    )
    pathlib.Path(str(saida) + ".fonte").write_text(
        (fonte.group(1).strip() if fonte else ""), encoding="utf-8"
    )
    pathlib.Path(str(saida) + ".origem").write_text(
        (origem.group(1).strip() if origem else "novidade"), encoding="utf-8"
    )
    print(post)


if __name__ == "__main__":
    main()
