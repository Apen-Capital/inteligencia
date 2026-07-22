-- Coluna de embedding (voyage-finance-2, 1024 dims) + funcao de busca por
-- similaridade de cosseno, usada pelo /api/chat (web/src/app/api/chat/route.ts).
alter table documentos add column embedding extensions.vector(1024);

create index if not exists documentos_embedding_idx
  on documentos
  using hnsw (embedding extensions.vector_cosine_ops);

create or replace function match_documentos(
  query_embedding extensions.vector(1024),
  match_count int default 5
)
returns table (
  id uuid,
  grupo text,
  fonte text,
  url text,
  titulo text,
  texto text,
  status text,
  data_coleta timestamptz,
  similaridade float
)
language sql
stable
as $$
  select
    documentos.id,
    documentos.grupo,
    documentos.fonte,
    documentos.url,
    documentos.titulo,
    documentos.texto,
    documentos.status,
    documentos.data_coleta,
    1 - (documentos.embedding <=> query_embedding) as similaridade
  from documentos
  where documentos.embedding is not null
  order by documentos.embedding <=> query_embedding
  limit match_count;
$$;
