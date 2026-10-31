# Atalho do iPhone: fotos da semana → gerador de posts

O iCloud Fotos não tem API pública. Por isso quem lê suas fotos é o próprio
iPhone, por um **Atalho** que roda sozinho toda terça às 8h:

1. pega as fotos dos últimos 7 dias (sem capturas de tela);
2. envia cada foto, reduzida, ao Claude, que devolve **uma frase** descrevendo a imagem;
3. descarta as fotos classificadas como "pessoal";
4. envia **só o texto** (data, local e descrição) para o GitHub, o que dispara o gerador.

As fotos **não** são salvas no GitHub. Elas passam apenas pela API do Claude
para gerar a descrição.

---

## Antes de começar: duas chaves

| Chave | Onde criar | Permissão |
|---|---|---|
| Chave da API do Claude | <https://platform.claude.com/settings/keys> (pode ser a mesma do secret `ANTHROPIC_API_KEY`) | — |
| Token do GitHub (fine-grained) | GitHub → Settings → Developer settings → **Fine-grained tokens** → Generate | Repositório: só `Meu-aplicativo-pessoal`. Permissão: **Actions → Read and write** |

---

## Montando o Atalho

Abra o app **Atalhos** → **+** → dê o nome **"Fotos para LinkedIn"** e adicione
as ações nesta ordem:

### 1. Buscar as fotos da semana
- **Buscar Fotos**
  - Adicionar Filtro: **Data da Captura** · *está nos últimos* · **7 dias**
  - Adicionar Filtro: **É Captura de Tela** · *é falso*
  - Ordenar por: **Data da Captura** · Mais Recente Primeiro
  - Limite: **ativado**, **15** fotos

### 2. Repetir com cada foto
- **Repetir com Cada** (item em: *Fotos*). Dentro do bloco:
  1. **Redimensionar Imagem**: *Item Repetido* para largura **768**
  2. **Converter Imagem**: para **JPEG** (qualidade ~60%)
  3. **Codificar em Base64**: Quebras de linha: **Nenhuma** ⚠️ (importante)
  4. **Obter Detalhes das Imagens**: **Data da Captura** de *Item Repetido*
  5. **Obter Detalhes das Imagens**: **Localização** de *Item Repetido*
  6. **Texto**: cole o conteúdo abaixo, trocando `BASE64` pela variável
     *Texto Codificado em Base64* (toque e segure → Selecionar Variável):

     ```json
     {"model":"claude-opus-5-5","max_tokens":1024,"output_config":{"effort":"low"},"fallbacks":"default","messages":[{"role":"user","content":[{"type":"image","source":{"type":"base64","media_type":"image/jpeg","data":"BASE64"}},{"type":"text","text":"Descreva esta foto em uma frase objetiva em portugues. Se parecer um evento profissional (palco, plateia, cracha, slides, estandes, banners, sala de treinamento), diga isso e transcreva nomes, logos e titulos legiveis. Se for uma foto pessoal (familia, comida, lazer, documentos, selfies casuais), responda apenas: pessoal"}]}]}
     ```
  7. **Obter Conteúdo do URL**
     - URL: `https://api.anthropic.com/v1/messages`
     - Método: **POST**
     - Cabeçalhos:
       - `x-api-key` → *sua chave do Claude*
       - `anthropic-version` → `2026-10-21`
       - `anthropic-beta` → `server-side-fallback-2026-07-01`
       - `content-type` → `application/json`
     - Corpo da Solicitação: **Arquivo** → variável *Texto* (do passo 6)
  8. **Obter Valor do Dicionário**: chave `content` em *Conteúdo do URL*
  9. **Obter Item da Lista**: **Último Item**
  10. **Obter Valor do Dicionário**: chave `text`
  11. **Se** *Valor do Dicionário* **não contém** `pessoal`:
      - **Texto**: `- [Data da Captura] · [Localização] · [Valor do Dicionário]`
      - **Adicionar à Variável**: nome **Descrições**
  12. (fim do Se)
- (fim do Repetir)

### 3. Enviar para o GitHub
- **Combinar Texto**: *Descrições* com **Nova Linha**
- **Obter Conteúdo do URL**
  - URL: `https://api.github.com/repos/souzabiancar-source/Meu-aplicativo-pessoal/actions/workflows/linkedin-gerar.yml/dispatches`
  - Método: **POST**
  - Cabeçalhos:
    - `Authorization` → `Bearer SEU_TOKEN_DO_GITHUB`
    - `Accept` → `application/vnd.github+json`
  - Corpo da Solicitação: **JSON**
    - `ref` (Texto) → `main`
    - `inputs` (Dicionário) → `eventos` (Texto) → variável *Texto Combinado*
- **Mostrar Notificação**: "Fotos enviadas, rascunho do LinkedIn a caminho ✍️"

Toque em ▶️ para testar. Em 1 a 2 minutos deve aparecer uma issue nova no repositório.

---

## Rodando sozinho toda terça

Atalhos → aba **Automação** → **+** → **Horário do Dia**
- **08:00**, **Semanalmente**, **Terça-feira**
- Marque **Executar Imediatamente** (sem pedir confirmação)
- Ação: **Executar Atalho** → *Fotos para LinkedIn*

Se o iPhone não rodar o Atalho, o GitHub gera o post às 9h mesmo assim,
usando suas ideias e as novidades de tecnologia.

## Privacidade e custo
- O texto enviado ao GitHub contém só data, local e descrição das fotos **não pessoais**.
- As chaves ficam guardadas apenas dentro do Atalho, no seu iPhone. Não compartilhe o Atalho com elas preenchidas.
- Custo aproximado: alguns centavos de dólar por semana para descrever até 15 fotos.
