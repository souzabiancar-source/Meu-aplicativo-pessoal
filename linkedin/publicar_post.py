"""Publica um texto no LinkedIn (perfil pessoal) pela API oficial de Posts.

Uso: python publicar_post.py <arquivo_com_texto>
Variáveis de ambiente:
  LINKEDIN_ACCESS_TOKEN  token OAuth com escopos `openid profile w_member_social` (obrigatório)
  LINKEDIN_PERSON_URN    (opcional) ex.: urn:li:person:AbC123 — descoberto automaticamente se vazio
  LINKEDIN_VERSION       (opcional) versão da API no formato AAAAMM
Imprime a URL do post publicado.
"""

import datetime
import os
import pathlib
import re
import sys

import requests

API = "https://api.linkedin.com"
# Caracteres reservados do formato "little text" usado em `commentary`.
RESERVADOS = re.compile(r"([\\|{}@\[\]()<>#*_~])")


def versao_api() -> str:
    if os.environ.get("LINKEDIN_VERSION"):
        return os.environ["LINKEDIN_VERSION"]
    # Versões são mensais e valem ~12 meses; usar a de 2 meses atrás é seguro.
    d = datetime.date.today().replace(day=1)
    for _ in range(2):
        d = (d - datetime.timedelta(days=1)).replace(day=1)
    return d.strftime("%Y%m")


def formatar(texto: str) -> str:
    """Escapa caracteres reservados e mantém hashtags clicáveis."""
    partes = re.split(r"(#\w+)", texto)
    saida = []
    for parte in partes:
        if re.fullmatch(r"#\w+", parte):
            saida.append("{hashtag|\\#|" + parte[1:] + "}")
        else:
            saida.append(RESERVADOS.sub(r"\\\1", parte))
    return "".join(saida)


def autor(token: str) -> str:
    urn = os.environ.get("LINKEDIN_PERSON_URN", "").strip()
    if urn:
        return urn
    r = requests.get(f"{API}/v2/userinfo", headers={"Authorization": f"Bearer {token}"}, timeout=30)
    r.raise_for_status()
    return f"urn:li:person:{r.json()['sub']}"


def publicar(texto: str) -> str:
    token = os.environ["LINKEDIN_ACCESS_TOKEN"]
    corpo = {
        "author": autor(token),
        "commentary": formatar(texto),
        "visibility": "PUBLIC",
        "distribution": {
            "feedDistribution": "MAIN_FEED",
            "targetEntities": [],
            "thirdPartyDistributionChannels": [],
        },
        "lifecycleState": "PUBLISHED",
        "isReshareDisabledByAuthor": False,
    }
    r = requests.post(
        f"{API}/rest/posts",
        json=corpo,
        headers={
            "Authorization": f"Bearer {token}",
            "LinkedIn-Version": versao_api(),
            "X-Restli-Protocol-Version": "2.0.0",
            "Content-Type": "application/json",
        },
        timeout=30,
    )
    if r.status_code == 401:
        sys.exit("Token do LinkedIn inválido ou expirado (eles duram 60 dias). Gere um novo e atualize o secret LINKEDIN_ACCESS_TOKEN.")
    if r.status_code >= 400:
        sys.exit(f"Erro {r.status_code} do LinkedIn: {r.text}")
    post_id = r.headers.get("x-restli-id", "")
    return f"https://www.linkedin.com/feed/update/{post_id}/" if post_id else "(publicado; ID não retornado)"


def main() -> None:
    texto = pathlib.Path(sys.argv[1]).read_text(encoding="utf-8").strip()
    if not texto:
        sys.exit("Texto do post vazio.")
    if len(texto) > 3000:
        sys.exit(f"Post com {len(texto)} caracteres; o limite do LinkedIn é 3.000.")
    print(publicar(texto))


if __name__ == "__main__":
    main()
