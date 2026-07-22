O time de inteligência hoje trabalha coletando informações externas de diversas fontes e tornando a absorção possivel pelo time da apen. 

A ideia principal é de buscar formas de automizar o processo de busca profunda e coleta de dados

Primeiro Passo é coleta e estruturação de dados com pesquisa profunda e login automático em plataformas que contem essas informações.
Segundo Passo é armazenamento de cada relatório com estrutura padronizada (para os três tipos) feito em um banco de dados acessivel ao time
Terceiro Passo é envio diário do relatório via email pro time de inteligência com um gatilho de envio para horário fixo
Quarto Passo é mensal: criação de relatorios macros tanto pro cliente quanto pro interno 
  --> Tipos de relatorio: 1. Diário; 2. Pro Cliente; 3. Pro interno.

## Fontes de dados

- Sites/portais de notícias e mercado
- Plataformas com login (assinatura/paga) — ex.: terminais financeiros, serviços de dados
- Redes sociais / fóruns
- Documentos regulatórios (CVM, Receita, etc.)

Inventário concreto das fontes hoje usadas pelo time (21 fontes, transcritas da planilha `Bases de dados para relatório.xlsx`): ver [`collector/sources.py`](collector/sources.py). São 4 grupos: Site de notícias (12), Portal de plataforma com login (3: XP, BTG, Nord Research), Dados de mercado (3: StreetStats, P/L da bolsa, CME FedWatch) e Canais de Youtube (3).

## Destinatários do envio diário

Lista fixa de emails internos do time de inteligência (a definir a lista exata — manter em arquivo de configuração, não hardcoded no código).

## Arquitetura

- **Banco de dados / infra**: **Supabase** (Postgres gerenciado, acesso via API/web para o time). Definido. Projeto ativo: `inteligencia` (org própria `marcuscav-apencapital`, região `us-west-2`) — ver "Decisões — Troca para conta Supabase própria" abaixo.
- **Estrutura dos relatórios**: não é definida por este time — vem de fora (a ser recebida/consumida como está).
- **Coleta de dados**: **Python** (definido). Sites de notícia via `httpx` + `trafilatura` (extração de texto principal); dados de mercado via snapshot de página; canais do YouTube via feed RSS público (sem API key). Login automático nas plataformas pagas (XP, BTG, Nord) ainda não implementado — ver "Decisões — Coleta automatizada" abaixo.
  - Credenciais de login **nunca** em texto puro no código/repositório — usar variáveis de ambiente/secrets manager.
- **Envio de email**: serviço/gatilho para disparo diário em horário fixo (cron ou scheduler).
- **Geração de relatórios macro mensais**: pipeline separado, para cliente e para uso interno.

## Decisões — Coleta automatizada (fontes abertas) — 2026-07-17

Contexto: o time ainda não tem acesso ao banco Supabase, então o trabalho atual é de tomada de decisão e prototipagem da coleta, não de produção.

- **Escopo do 1º protótipo**: só as 18 fontes que não exigem login (notícias + dados de mercado + YouTube). As 3 plataformas pagas (XP, BTG, Nord Research) ficam mapeadas em `collector/sources.py` mas **não implementadas** — exigem gestão de credenciais (env vars/secrets), que é um passo à parte.
- **Paywalls conhecidos**: FT, WSJ, Bloomberg Línea e Valor Econômico não estão marcados como "Precisa de login" na planilha original, mas têm paywall conhecido. O coletor trata isso como status `"parcial"` (texto extraído muito curto), não como erro/bug.
- **RAG / embeddings: adiado.** Nesta etapa só coletamos e estruturamos os documentos brutos (texto + metadados, ver schema em `collector/common.py`). A escolha do provedor de embeddings fica para quando o Supabase (pgvector) estiver acessível. Opção já pesquisada: **Voyage AI** é a parceira oficial da Anthropic para embeddings, com modelo específico para o setor financeiro ([Embeddings - Claude Docs](https://docs.claude.com/en/docs/build-with-claude/embeddings)) — alternativa a um modelo local/offline. Ainda não decidido.
- **Armazenamento temporário**: sem acesso ao Supabase, os documentos coletados são salvos localmente em `data/raw/<data>/*.json` — pasta no `.gitignore`, **não comitada** (conteúdo de terceiros, questão de direitos autorais).
- **Etiqueta de scraping**: delay entre requisições e User-Agent identificável (ver `collector/common.py`).
- **Limitação observada na 1ª rodada**: coletar a *home* de sites de notícia (InfoMoney, CNN Brasil etc.) traz principalmente menu/navegação, não o conteúdo do dia — extrair artigos específicos exige descobrir links de matérias primeiro (crawling), não só ler a home. Fica como próximo passo. Também confirmado na prática: The Economist, FT, WSJ e Reuters bloqueiam requisições automatizadas (403/401), além do paywall.

## Decisões — Supabase e Front — 2026-07-18

- **Supabase real, projeto próprio**: durante a investigação, descobrimos que o MCP do Supabase já conectado neste ambiente é a conta oficial da empresa (org de `eduardoramos@apencapital.com.br`, confirmado com ele) — não uma conta pessoal. Essa org já tinha um projeto `pipeline_iniciativas` com tabelas de um app não relacionado (`usuarios`, `iniciativas`, etc.) — por isso criamos um **projeto novo e separado**, `apen-inteligencia` (região `sa-east-1`, custo US$ 0/mês), para não misturar schemas.
- **Schema inicial**: tabela `documentos` (mesmo formato usado pelo coletor Python — grupo, fonte, url, título, texto, status, datas). RLS habilitada, com leitura pública (dado é notícia pública, sem PII de cliente) e sem policy de insert pública — só o coletor Python (via `service_role`) grava. Extensão `pgvector` já habilitada, sem uso ainda (prepara pro RAG futuro).
- **Coletor Python grava no Supabase**: `collector/supabase_sink.py` faz um `insert` simples de cada documento coletado (log append-only — não há upsert nem constraint única além do `id`; reexecutar o coletor no mesmo dia gera novas linhas em vez de atualizar as existentes, ver TODO em `supabase_sink.py`), além de manter o JSON local. Sem `SUPABASE_SERVICE_ROLE_KEY` configurada em `.env`, a gravação é pulada com aviso (a coleta local continua funcionando normalmente).
- **Front básico (`web/`)**: Next.js + shadcn/ui + Tailwind, duas abas:
  - **Gestão de Relatórios** (`/relatorios`): lista os documentos brutos da tabela `documentos` — não uma estrutura de relatório final, que ainda não foi recebida.
  - **Chat Bot** (`/chat`): interface pronta; o backend (`/api/chat`) é um stub até a integração real com Voyage AI (busca semântica) existir.
- **Auth**: nenhuma nesta 1ª versão — ferramenta interna, sem dado sensível de cliente ainda. Reavaliar (Supabase Auth restrito a `@apencapital.com.br`) antes de qualquer deploy público.
- **Guia rápido — Voyage AI** (ação da pessoa dona da chave, não do assistente):
  1. Criar conta/logar em [dashboard.voyageai.com](https://dashboard.voyageai.com).
  2. Gerar uma API key na seção "API Keys".
  3. Colar o valor direto em `.env` (Python, campo `VOYAGE_API_KEY`) e/ou `web/.env.local` — **nunca no chat com o assistente**.
  4. Free tier vigente na época da pesquisa: 50M tokens grátis no `voyage-finance-2` — conferir valor atual em [docs.voyageai.com/docs/pricing](https://docs.voyageai.com/docs/pricing) antes de assumir.
  5. A integração de verdade (embeddings dos documentos + busca semântica no `/api/chat`) é um próximo passo, depois que a chave existir.

## Decisões — Revisão final pré-lançamento — 2026-07-19

Varredura completa do código (coletor + Supabase + front), com achados verificados adversarialmente antes de qualquer correção ser aplicada. 11 problemas reais corrigidos, entre eles: falha no coletor que derrubava a coleta inteira se a gravação no Supabase desse erro; documento de erro incompleto quando um fetcher lançava exceção não tratada; `data_coleta` sendo descartado antes do insert no Supabase; modo escuro completamente inerte no front (classes `dark:` nunca ativavam); `/api/chat` retornando erro 500 cru para corpo inválido em vez de 400; chat não mostrava a mensagem de erro real da API; duplicação de código entre os 3 fetchers eliminada com um helper único (`baixar_pagina` em `collector/common.py`).

Também corrigido ao vivo no Supabase: a extensão `pgvector` estava no schema `public` (WARN de segurança do próprio Supabase Advisor) — movida para um schema `extensions` dedicado, sem perda de dado (tabela ainda não usa colunas vetoriais).

**Decisões que ficaram em aberto, para o dono do projeto (não implementadas de forma unilateral):**
- **Modo escuro**: hoje segue automaticamente o SO/navegador do usuário (`prefers-color-scheme`). Se quiser um toggle manual em vez disso, precisa de um `ThemeProvider` (ex. `next-themes`) — não implementado, é decisão de UX.
- **Modelo de dados da tabela `documentos`**: hoje é um log append-only (cada execução do coletor insere novas linhas, mesmo repetindo fonte no mesmo dia). Se o certo for "um snapshot por fonte por dia", precisa de uma migração de schema (índice único + trocar `insert` por `upsert`) — ver TODO em `collector/supabase_sink.py`.
- **Autenticação do front**: continua sem auth (ver acima). Não implementada nesta revisão por ser decisão de produto, não bug.
- **Rate limiting em `/api/chat`**: inofensivo hoje (endpoint é stub, sem custo), mas vira risco real de abuso assim que a integração com Voyage AI/LLM for ligada — sinalizado para quando isso acontecer.
- **`web/README.md`** continua sendo o boilerplate padrão do `create-next-app`, sem customização — cosmético, não bloqueia lançamento.

## Decisões — Troca para conta Supabase própria — 2026-07-22

- **Motivo da troca**: o projeto `apen-inteligencia` vivia na conta pessoal do Eduardo (org `eduardoramos@apencapital.com.br`), usada só porque era a conta conectada no ambiente na época. Decidimos migrar para uma conta própria do projeto: `marcuscav-apencapital`. O projeto antigo foi removido (fora do nosso controle, constatado já removido — não havia dado real nele, então sem perda).
- **Projeto novo**: `inteligencia` (id `oxwzoeujpyumnbmidwwe`, região `us-west-2` — nota: diferente do `sa-east-1` do projeto anterior; dado é notícia pública/scraping, não há requisito de residência de dados no Brasil identificado até agora, mas vale revisitar se isso mudar). Já conectado ao repositório GitHub do projeto pelo próprio Supabase.
- **Conexão isolada por projeto**: em vez do conector de conta do claude.ai (que é global, vale para todos os projetos do usuário), configuramos um servidor MCP dedicado (`supabase-inteligencia`, escopo `local` no Claude Code — arquivo `~/.claude.json`, não versionado) com um Personal Access Token da conta `marcuscav-apencapital`. Isso isola o acesso Supabase deste projeto de qualquer outro projeto na mesma máquina.
- **Schema recriado do zero**: mesma tabela `documentos` + RLS de leitura pública, `pgvector` já instalado direto no schema `extensions` (evitando o WARN de segurança que corrigimos manualmente da vez passada). SQL versionado em [`supabase/migrations/20260722000000_criar_tabela_documentos.sql`](supabase/migrations/20260722000000_criar_tabela_documentos.sql).
- **Achado novo, não resolvido**: o Supabase Advisor aponta um WARN sobre uma função `public.rls_auto_enable()` (provisionada pelo próprio Supabase, liga RLS automaticamente em tabelas novas — mecanismo de proteção, não algo que criamos) ser executável via RPC por `anon`/`authenticated`. Tentei revogar essa permissão e fui bloqueado pelo classificador de segurança do Claude Code (mudança de permissão fora do escopo do que este projeto criou). Baixo risco, mas fica registrado — avaliar com calma se vale revogar manualmente.

## Decisões — Integração real com Voyage AI e redesign visual — 2026-07-22

- **Busca semântica real, de ponta a ponta**: `documentos` ganhou coluna `embedding vector(1024)` (modelo `voyage-finance-2`) + índice HNSW + função `match_documentos` (busca por similaridade de cosseno) — ver [`supabase/migrations/20260722010000_adicionar_embedding_e_match_function.sql`](supabase/migrations/20260722010000_adicionar_embedding_e_match_function.sql).
  - `collector/embeddings.py`: gera o embedding de cada documento coletado (chamada direta à API REST da Voyage, sem SDK extra) — integrado a `supabase_sink.py`, roda automaticamente a cada coleta.
  - `collector/backfill_embeddings.py`: preenche embedding dos documentos já gravados sem ele (rodar quando necessário: `python -m collector.backfill_embeddings`). **Tem rate limit baixo na Voyage** (429 em contas novas) — o script já tem delay de 15s entre chamadas; rodar mais de uma vez se sobrar algum documento sem embedding.
  - `/api/chat` agora embeda a pergunta do usuário e busca os 5 documentos mais similares de verdade — testado ao vivo, retornando resultados reais com score de similaridade.
- **Geração de resposta em linguagem natural: ainda não implementada, por decisão do usuário.** A Voyage só faz embeddings/busca — gerar uma resposta em texto corrido exigiria uma chave de API da Anthropic (`ANTHROPIC_API_KEY`, obtida em console.anthropic.com, **independente** da conta/assinatura Claude Pro do claude.ai — não consome o limite de mensagens do Pro). Sem essa chave, o chat mostra os trechos mais relevantes encontrados (fonte, título, trecho, similaridade), sem fingir uma resposta gerada.
- **Redesign visual completo** (via skill `/frontend-design`): identidade própria de "terminal de inteligência financeira" — fundo grafite-marinho quase preto (`#0B0E14`) com acento dourado-latão (`#C89B3C`), tipografia Fraunces (títulos, serifada editorial) + IBM Plex Sans (corpo) + IBM Plex Mono (dados/status). **Tema escuro fixo, por decisão de design** (não segue mais o SO/navegador — decisão anterior revista: o tom de terminal não funcionaria bem em tema claro). Elemento de assinatura: uma ticker tape rolando manchetes reais coletadas (fonte — título) no topo de toda página. Componentes shadcn não usados (`avatar`, `separator`, `table`, `tabs`, `scroll-area`, `card`) foram removidos.

## Próximos passos

1. Mapear lista completa de plataformas/fontes por tipo de relatório. ✅ feito para as fontes hoje usadas (`collector/sources.py`); reavaliar quando surgirem novas fontes.
2. Escolher stack de coleta de dados (linguagem/framework) e mecanismo de agendamento. ✅ Python decidido; agendamento (cron/scheduler) ainda em aberto.
3. Definir lista de destinatários e horário fixo de envio.
4. Implementar coleta das 3 plataformas com login (XP, BTG, Nord) — definir gestão de credenciais.
5. ✅ `SUPABASE_SERVICE_ROLE_KEY` preenchida — coletor grava e embeda de verdade no Supabase (18 documentos, 12 com embedding).
6. ✅ Busca semântica real via Voyage AI implementada no `/api/chat`.
7. Configurar `ANTHROPIC_API_KEY` (console.anthropic.com) para gerar respostas em linguagem natural a partir dos documentos recuperados — próximo passo do chat.
8. Definir autenticação do front antes de qualquer deploy público.
9. Decidir o modelo de dados de `documentos` (log append-only vs. upsert por snapshot) — ver seção "Revisão final pré-lançamento" acima.
