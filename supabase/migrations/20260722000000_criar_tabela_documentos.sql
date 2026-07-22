-- Tabela documentos: espelha o schema gravado pelo coletor Python
-- (collector/common.py:montar_documento). RLS com leitura pública (dado é
-- notícia pública, sem PII de cliente); só o coletor Python, via
-- service_role, grava (sem policy de insert para anon/authenticated).
create schema if not exists extensions;
create extension if not exists vector schema extensions;

create table documentos (
  id uuid primary key default gen_random_uuid(),
  grupo text not null,
  fonte text not null,
  url text not null,
  titulo text,
  texto text,
  data_coleta timestamptz not null default now(),
  data_publicacao text,
  status text not null,
  detalhe text
);

alter table documentos enable row level security;

create policy "leitura publica" on documentos
  for select
  using (true);
