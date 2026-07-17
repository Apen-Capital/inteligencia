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

## Destinatários do envio diário

Lista fixa de emails internos do time de inteligência (a definir a lista exata — manter em arquivo de configuração, não hardcoded no código).

## Arquitetura

- **Banco de dados / infra**: **Supabase** (Postgres gerenciado, acesso via API/web para o time). Definido.
- **Estrutura dos relatórios**: não é definida por este time — vem de fora (a ser recebida/consumida como está).
- **Coleta de dados**: mecanismo de scraping/pesquisa profunda + login automático nas plataformas pagas — stack a definir por nós (ver Próximos passos).
  - Credenciais de login **nunca** em texto puro no código/repositório — usar variáveis de ambiente/secrets manager.
- **Envio de email**: serviço/gatilho para disparo diário em horário fixo (cron ou scheduler).
- **Geração de relatórios macro mensais**: pipeline separado, para cliente e para uso interno.

## Próximos passos

1. Mapear lista completa de plataformas/fontes por tipo de relatório.
2. Escolher stack de coleta de dados (linguagem/framework) e mecanismo de agendamento.
3. Definir lista de destinatários e horário fixo de envio.
