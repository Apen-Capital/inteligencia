# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Status do projeto

Protótipo com busca semântica real de ponta a ponta. Coleta em Python (`collector/`) grava na tabela `documentos` do Supabase (projeto `inteligencia`) e gera embeddings via Voyage AI (`voyage-finance-2`) automaticamente. `/api/chat` embeda a pergunta do usuário e busca os documentos mais similares via `pgvector` — testado ao vivo, funcionando. **Falta só a geração de resposta em linguagem natural** (precisa de `ANTHROPIC_API_KEY`, ainda não configurada — decisão do usuário de seguir sem isso por enquanto); até lá o chat mostra os trechos recuperados, não uma resposta gerada. Front redesenhado (`/frontend-design`, 2026-07-22): tema escuro fixo, tipografia Fraunces/IBM Plex, ticker de manchetes reais como assinatura visual. Estrutura final dos relatórios ainda não foi recebida (ver README.md).

## Comandos

Coletor (Python):
```bash
python -m venv .venv
.venv/Scripts/activate   # Windows (bash: source .venv/Scripts/activate)
pip install -r requirements.txt

python -m collector.run                    # roda o protótipo de coleta (fontes abertas), grava no Supabase e gera embeddings
python -m collector.sources                 # imprime o inventário de fontes por grupo
python -m collector.backfill_embeddings     # gera embedding para documentos já gravados que ainda não têm (rodar de novo se sobrar algum — a Voyage tem rate limit baixo em conta nova, 429)
```
Requer `.env` (copiar de `.env.example`) com `SUPABASE_URL`/`SUPABASE_SERVICE_ROLE_KEY` para gravar no Supabase, e `VOYAGE_API_KEY` para gerar embeddings — sem elas, a etapa correspondente é pulada com aviso (nunca quebra a coleta local).

Front (Next.js, em `web/`):
```bash
cd web
npm install
npm run dev     # http://localhost:3000 — abas /relatorios e /chat
npm run build   # build de produção (usado para checar erros de tipo/lint)
```
Requer `web/.env.local` (copiar de `web/.env.local.example`) com `NEXT_PUBLIC_SUPABASE_URL`/`NEXT_PUBLIC_SUPABASE_ANON_KEY`.

Não há testes automatizados configurados ainda neste protótipo (lint do Next.js roda via `npm run build`).

## Arquitetura do coletor (`collector/`)

- `sources.py` — fonte única de verdade: `dataclass Fonte` + lista `FONTES` (21 fontes, 4 grupos), transcrita da planilha `Bases de dados para relatório.xlsx`. `fontes_mvp()` retorna só as 18 sem `requer_login`.
- `common.py` — schema do documento salvo (`montar_documento`), `slugify`, `HEADERS`/User-Agent do coletor, e `baixar_pagina()` (GET padrão com tratamento de erro — helper compartilhado pelos 3 fetchers, evita duplicação).
- `fetchers/article_fetcher.py` — sites de notícia: `baixar_pagina` + `trafilatura`. Texto curto/vazio ⇒ status `"parcial"` (heurística de paywall), nunca lança exceção para fora.
- `fetchers/market_data_fetcher.py` — páginas de dados de mercado: snapshot de texto bruto (parsing do dado específico de cada página ainda não implementado).
- `fetchers/youtube_fetcher.py` — resolve `channel_id`/`playlist_id` a partir da URL (sem API key) e lê o feed RSS público do YouTube para listar uploads recentes.
- `run.py` — orquestrador (`python -m collector.run`): despacha cada fonte de `fontes_mvp()` para o fetcher do seu grupo, aplica delay entre requisições, salva cada resultado em `data/raw/<AAAA-MM-DD>/<fonte-slug>.json`, grava no Supabase (`salvar_documento`, com try/except próprio — uma falha de gravação não derruba a coleta das fontes seguintes) e imprime um resumo ok/parcial/erro. **`data/` não é versionado** (conteúdo de terceiros).
- As 3 fontes com login (XP, BTG, Nord) aparecem em `sources.py` mas são puladas pelo `run.py` — implementá-las exige decidir gestão de credenciais primeiro.
- `supabase_sink.py` — grava cada documento na tabela `documentos` do Supabase via `service_role` key (env var); pulado (com aviso, sem quebrar a coleta local) se as credenciais não estiverem em `.env`. Faz `insert` simples (log append-only, sem upsert/constraint única — ver TODO no arquivo, decisão de produto em aberto). Inclui o embedding (via `embeddings.gerar_embedding`) no mesmo insert.
- `embeddings.py` — chama a API REST da Voyage AI diretamente (`voyage-finance-2`, sem SDK) para gerar o vetor de embedding de um texto. Retorna `None` (não lança exceção) se `VOYAGE_API_KEY` ausente, texto vazio, ou a chamada falhar.
- `backfill_embeddings.py` — script standalone (`python -m collector.backfill_embeddings`) que gera embedding pra documentos já no Supabase sem um. Delay de 15s entre chamadas — a Voyage tem rate limit baixo em contas novas (429); rodar de novo se sobrar algum.

## Arquitetura do front (`web/`)

Next.js (App Router) + shadcn/ui + Tailwind. Sem autenticação nesta versão (reavaliar antes de deploy público). Identidade visual própria desde 2026-07-22 (via skill `/frontend-design`) — ver seção de design abaixo.

- `src/lib/supabase.ts` — client Supabase (browser/server, chave publicável) + tipo `Documento`.
- `src/lib/voyage.ts` — `embedarConsulta()`: chama a API REST da Voyage direto (fetch nativo, sem SDK) pra gerar o embedding da pergunta do usuário.
- `src/components/ticker.tsx` — Server Component que busca as manchetes mais recentes (`fonte`+`titulo`) e renderiza a ticker tape (elemento de assinatura do design, ver `globals.css`/`.ticker-track`).
- `src/app/relatorios/page.tsx` — aba "Gestão de Relatórios": Server Component, lê a tabela `documentos` direto (RLS permite leitura pública). Mostra os documentos brutos coletados, não uma estrutura de relatório final (que ainda não existe).
- `src/app/chat/page.tsx` + `src/components/chat-client.tsx` — aba "Chat": UI com histórico + input; renderiza os resultados da busca semântica (fonte, título, trecho, similaridade) além da mensagem de status.
- `src/app/api/chat/route.ts` — **busca semântica real**: valida corpo (400 em JSON inválido/não-objeto/campo ausente) → `embedarConsulta()` (Voyage) → RPC `match_documentos` no Supabase → retorna `{ resposta, resultados[] }`. Sem `VOYAGE_API_KEY`, cai no aviso antigo (stub). **Geração de resposta em linguagem natural via Claude ainda não implementada** — falta `ANTHROPIC_API_KEY` (decisão do usuário, não bug).
- `src/app/globals.css` — tema escuro fixo (não segue mais o SO — decisão de design revista em 2026-07-22), tokens de cor/fonte do redesign, animação da ticker tape (`prefers-reduced-motion` respeitado).

## Identidade visual (`web/`)

"Terminal de inteligência financeira" — fundo `#0B0E14`, superfícies `#12161F`, acento dourado-latão `#C89B3C` (não o verde/vermelho neon padrão de tema escuro), status semânticos via `--color-status-{ok,parcial,erro}` (definidos em `globals.css`, usados com `variant="outline"` do `Badge`, não os variants genéricos default/secondary/destructive). Fraunces (`font-display`, títulos), IBM Plex Sans (`font-sans`, corpo), IBM Plex Mono (`font-mono`, dados/timestamps/status). Tema escuro é fixo (não alterna com o SO). Componentes shadcn não usados no app foram removidos (`avatar`, `card`, `scroll-area`, `separator`, `table`, `tabs`) — só `badge`, `button`, `textarea` continuam.

## O que este projeto faz

Automatiza o trabalho do time de inteligência da Apen Capital, que hoje coleta manualmente informações externas (mercado, notícias, plataformas pagas, redes sociais, dados regulatórios) para o time.

Fluxo em 4 passos:
1. Coleta/estruturação de dados — pesquisa profunda + login automático em plataformas pagas.
2. Armazenamento padronizado dos relatórios em banco de dados. Três tipos de relatório: **Diário**, **Pro Cliente**, **Pro Interno**.
3. Envio diário por email ao time, em horário fixo (cron/scheduler).
4. Mensal: geração de relatórios macro (cliente e interno).

## Decisões de arquitetura já tomadas

- **Banco de dados/infra**: Supabase (Postgres gerenciado). Definido — não reabrir essa decisão sem confirmar com o usuário. Projeto ativo: `inteligencia` (id `oxwzoeujpyumnbmidwwe`, org própria `marcuscav-apencapital`, região `us-west-2`) — substituiu o projeto anterior (`apen-inteligencia`, na conta do Eduardo, já removido). Acesso via servidor MCP dedicado `supabase-inteligencia` (escopo local, token próprio — não o conector de conta global do claude.ai).
- **Estrutura dos relatórios**: vem de fora do time, não é definida por este projeto — deve ser consumida como recebida, não redesenhada.
- **Coleta de dados**: Python (definido). Scraping leve (`httpx`+`trafilatura`) para sites/dados de mercado, feed RSS para YouTube. Login automático em plataformas pagas ainda não implementado.
- **Credenciais de login**: nunca em texto puro no código/repositório. Usar variáveis de ambiente/secrets manager.
- **Destinatários do envio diário**: lista fixa de emails do time de inteligência, mantida em arquivo de configuração — nunca hardcoded no código.

## Próximos passos (em aberto, ver README.md)

1. Configurar `ANTHROPIC_API_KEY` (console.anthropic.com, independente da conta claude.ai) para implementar a geração de resposta em linguagem natural no `/api/chat` — hoje só mostra os documentos recuperados.
2. Definir lista de destinatários e horário fixo de envio do relatório diário.
3. Definir autenticação do front antes de qualquer deploy público.
4. Decidir modelo de dados de `documentos` (log append-only vs. upsert por snapshot — ver TODO em `supabase_sink.py`).

## Skills configuradas no projeto

Habilitadas em `.claude/settings.json` (escopo *project*, compartilhado com quem clonar o repo):

- `skill-creator`, `frontend-design`, `supabase` (inclui supabase-postgres-best-practices), `vercel` (inclui react-best-practices e shadcn), `example-skills@anthropic-agent-skills` (inclui webapp-testing), `playwright` (MCP de browser automation), `superpowers@claude-plugins-official`.
- Skill manual (sem mecanismo de plugin/marketplace) em `.claude/skills/install-skills/`: meta-skill para buscar/instalar novas skills a partir de repositórios GitHub. Node.js foi instalado depois (usado pelo front em `web/`); o CLI `skills.sh`/`npx add-skill` passa a ser uma opção viável, mas o fallback via `git clone` puro continua funcionando.
