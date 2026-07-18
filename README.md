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

- **Banco de dados / infra**: **Supabase** (Postgres gerenciado, acesso via API/web para o time). Definido. Projeto ativo: `apen-inteligencia` (org da empresa, região `sa-east-1`) — ver "Decisões — Supabase e Front" abaixo.
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
- **Coletor Python grava no Supabase**: `collector/supabase_sink.py` faz upsert de cada documento coletado, além de manter o JSON local. Sem `SUPABASE_SERVICE_ROLE_KEY` configurada em `.env`, a gravação é pulada com aviso (a coleta local continua funcionando normalmente).
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

## Próximos passos

1. Mapear lista completa de plataformas/fontes por tipo de relatório. ✅ feito para as fontes hoje usadas (`collector/sources.py`); reavaliar quando surgirem novas fontes.
2. Escolher stack de coleta de dados (linguagem/framework) e mecanismo de agendamento. ✅ Python decidido; agendamento (cron/scheduler) ainda em aberto.
3. Definir lista de destinatários e horário fixo de envio.
4. Implementar coleta das 3 plataformas com login (XP, BTG, Nord) — definir gestão de credenciais.
5. Preencher `SUPABASE_SERVICE_ROLE_KEY` em `.env` e rodar `python -m collector.run` para popular a tabela `documentos` com dados reais.
6. Configurar `VOYAGE_API_KEY` e implementar a busca semântica real no `/api/chat` (embeddings dos documentos coletados).
7. Definir autenticação do front antes de qualquer deploy público.
