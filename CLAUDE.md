# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Status do projeto

Protótipo funcional: coleta em Python (`collector/`) grava na tabela `documentos` de um Supabase real (projeto `apen-inteligencia`), e um front básico em Next.js (`web/`) lê essa tabela. Estrutura final dos relatórios ainda não foi recebida (ver README.md) e o RAG/chat real depende da Voyage AI (ainda não configurada) — ver README.md, seção "Decisões — Supabase e Front".

## Comandos

Coletor (Python):
```bash
python -m venv .venv
.venv/Scripts/activate   # Windows (bash: source .venv/Scripts/activate)
pip install -r requirements.txt

python -m collector.run          # roda o protótipo de coleta (fontes abertas) e grava no Supabase
python -m collector.sources       # imprime o inventário de fontes por grupo
```
Requer `.env` (copiar de `.env.example`) com `SUPABASE_URL`/`SUPABASE_SERVICE_ROLE_KEY` para gravar no Supabase — sem isso, só salva local em `data/raw/`.

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
- `common.py` — schema do documento salvo (`montar_documento`), `slugify`, `HEADERS`/User-Agent do coletor.
- `fetchers/article_fetcher.py` — sites de notícia: `httpx` + `trafilatura`. Texto curto/vazio ⇒ status `"parcial"` (heurística de paywall), nunca lança exceção para fora.
- `fetchers/market_data_fetcher.py` — páginas de dados de mercado: snapshot de texto bruto (parsing do dado específico de cada página ainda não implementado).
- `fetchers/youtube_fetcher.py` — resolve `channel_id`/`playlist_id` a partir da URL (sem API key) e lê o feed RSS público do YouTube para listar uploads recentes.
- `run.py` — orquestrador (`python -m collector.run`): despacha cada fonte de `fontes_mvp()` para o fetcher do seu grupo, aplica delay entre requisições, salva cada resultado em `data/raw/<AAAA-MM-DD>/<fonte-slug>.json` e imprime um resumo ok/parcial/erro. **`data/` não é versionado** (conteúdo de terceiros).
- As 3 fontes com login (XP, BTG, Nord) aparecem em `sources.py` mas são puladas pelo `run.py` — implementá-las exige decidir gestão de credenciais primeiro.
- `supabase_sink.py` — grava cada documento na tabela `documentos` do Supabase via `service_role` key (env var); pulado (com aviso, sem quebrar a coleta local) se as credenciais não estiverem em `.env`.

## Arquitetura do front (`web/`)

Next.js (App Router) + shadcn/ui + Tailwind. Sem autenticação nesta versão (reavaliar antes de deploy público).

- `src/lib/supabase.ts` — client Supabase (browser/server, chave publicável) + tipo `Documento`.
- `src/app/relatorios/page.tsx` — aba "Gestão de Relatórios": Server Component, lê a tabela `documentos` direto (RLS permite leitura pública). Mostra os documentos brutos coletados, não uma estrutura de relatório final (que ainda não existe).
- `src/app/chat/page.tsx` + `src/components/chat-client.tsx` — aba "Chat Bot": UI completa (histórico + input).
- `src/app/api/chat/route.ts` — stub: responde avisando que a integração real (busca semântica via Voyage AI) ainda não existe. Implementar de verdade é o próximo passo, depois que `VOYAGE_API_KEY` estiver configurada.

## O que este projeto faz

Automatiza o trabalho do time de inteligência da Apen Capital, que hoje coleta manualmente informações externas (mercado, notícias, plataformas pagas, redes sociais, dados regulatórios) para o time.

Fluxo em 4 passos:
1. Coleta/estruturação de dados — pesquisa profunda + login automático em plataformas pagas.
2. Armazenamento padronizado dos relatórios em banco de dados. Três tipos de relatório: **Diário**, **Pro Cliente**, **Pro Interno**.
3. Envio diário por email ao time, em horário fixo (cron/scheduler).
4. Mensal: geração de relatórios macro (cliente e interno).

## Decisões de arquitetura já tomadas

- **Banco de dados/infra**: Supabase (Postgres gerenciado). Definido — não reabrir essa decisão sem confirmar com o usuário. Projeto ativo: `apen-inteligencia` (org oficial da empresa, região `sa-east-1`) — projeto separado do `pipeline_iniciativas` (outro app, mesma org), para não misturar schemas.
- **Estrutura dos relatórios**: vem de fora do time, não é definida por este projeto — deve ser consumida como recebida, não redesenhada.
- **Coleta de dados**: Python (definido). Scraping leve (`httpx`+`trafilatura`) para sites/dados de mercado, feed RSS para YouTube. Login automático em plataformas pagas ainda não implementado.
- **Credenciais de login**: nunca em texto puro no código/repositório. Usar variáveis de ambiente/secrets manager.
- **Destinatários do envio diário**: lista fixa de emails do time de inteligência, mantida em arquivo de configuração — nunca hardcoded no código.

## Próximos passos (em aberto, ver README.md)

1. Preencher `SUPABASE_SERVICE_ROLE_KEY` em `.env` e rodar `python -m collector.run` para popular `documentos` com dados reais.
2. Configurar `VOYAGE_API_KEY` e implementar busca semântica real no `/api/chat`.
3. Definir lista de destinatários e horário fixo de envio do relatório diário.
4. Definir autenticação do front antes de qualquer deploy público.

## Skills configuradas no projeto

Habilitadas em `.claude/settings.json` (escopo *project*, compartilhado com quem clonar o repo):

- `skill-creator`, `frontend-design`, `supabase` (inclui supabase-postgres-best-practices), `vercel` (inclui react-best-practices e shadcn), `example-skills@anthropic-agent-skills` (inclui webapp-testing), `playwright` (MCP de browser automation), `superpowers@claude-plugins-official`.
- Skill manual (sem mecanismo de plugin/marketplace) em `.claude/skills/install-skills/`: meta-skill para buscar/instalar novas skills a partir de repositórios GitHub. Node.js foi instalado depois (usado pelo front em `web/`); o CLI `skills.sh`/`npx add-skill` passa a ser uma opção viável, mas o fallback via `git clone` puro continua funcionando.
