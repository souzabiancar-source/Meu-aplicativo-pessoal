# Posts automáticos no LinkedIn

Toda **terça de manhã** o Claude escolhe um assunto nesta ordem:

1. 📸 **Evento nas suas fotos**: um Atalho do iPhone descreve as fotos da semana ([guia](atalho-iphone.md));
2. 💬 **Ideias das suas conversas**: anotadas em [`contexto/ideias.md`](contexto/ideias.md);
3. 📰 **Últimas novidades de tecnologia e inovação**: pesquisadas na web.

Depois escreve um post no seu estilo e abre uma **issue** neste
repositório com o rascunho. Você revisa e, se gostar, adiciona a etiqueta
**`aprovado`**: o post é publicado no seu perfil e a issue é fechada com o link.

```
terça 9h ──► Claude gera rascunho ──► issue "LinkedIn: ..." ──► você edita/aprova ──► publicado
```

## Configuração (uma vez só)

### 1. Chave da API do Claude
Crie em <https://platform.claude.com/settings/keys> e salve como secret
`ANTHROPIC_API_KEY` em **Settings → Secrets and variables → Actions → New repository secret**.

### 2. Token do LinkedIn
1. Acesse <https://www.linkedin.com/developers/apps> e crie um app (é preciso
   associar a uma Página do LinkedIn; pode criar uma página simples).
2. Na aba **Products**, adicione **"Share on LinkedIn"** e
   **"Sign In with LinkedIn using OpenID Connect"**.
3. Abra o **OAuth Token Generator Tool**
   (<https://www.linkedin.com/developers/tools/oauth/token-generator>), escolha o app
   e marque os escopos `openid`, `profile` e `w_member_social`. Gere o token.
4. Salve o token como secret `LINKEDIN_ACCESS_TOKEN`.

> ⚠️ O token do LinkedIn **expira em 60 dias**. Quando vencer, a publicação
> falha com uma mensagem avisando; basta gerar outro e atualizar o secret.

### 3. Atalho do iPhone (fotos)
Siga o [guia do Atalho](atalho-iphone.md). É opcional: sem ele, o gerador usa as ideias e as novidades.

### 4. Personalize sua voz
Edite [`perfil.md`](perfil.md) — principalmente a seção **"Quem eu sou"**.

## Uso no dia a dia
- **Aprovar:** adicione a etiqueta `aprovado` na issue.
- **Ajustar antes:** edite o texto entre `<!-- POST_INICIO -->` e `<!-- POST_FIM -->` e depois aprove.
- **Descartar:** feche a issue.
- **Gerar um post agora:** aba **Actions → "LinkedIn - gerar rascunho" → Run workflow**
  (dá para passar um direcionamento, ex.: "IA na educação").
- **Mudar o dia/horário:** altere o `cron` em `.github/workflows/linkedin-gerar.yml`.

## Custos
Cada post usa uma chamada ao Claude com busca na web — normalmente alguns
centavos de dólar. As GitHub Actions são gratuitas dentro da cota do plano.
