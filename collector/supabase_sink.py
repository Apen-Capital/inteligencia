# -*- coding: utf-8 -*-
"""Grava os documentos coletados na tabela `documentos` do Supabase.

Lê as credenciais de variáveis de ambiente (arquivo .env, nunca commitado).
Se SUPABASE_URL/SUPABASE_SERVICE_ROLE_KEY não estiverem configuradas, a
gravação é pulada com um aviso — a coleta local (JSON) continua funcionando
normalmente, sem depender do Supabase.
"""

import os

from dotenv import load_dotenv

from .embeddings import gerar_embedding

load_dotenv()

_AVISO_JA_MOSTRADO = False


def _client():
    global _AVISO_JA_MOSTRADO
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

    if not url or not key:
        if not _AVISO_JA_MOSTRADO:
            print("[supabase_sink] SUPABASE_URL/SUPABASE_SERVICE_ROLE_KEY não configuradas — pulando gravação no Supabase (só salvando local).")
            _AVISO_JA_MOSTRADO = True
        return None

    from supabase import create_client
    return create_client(url, key)


def salvar_documento(documento: dict) -> None:
    """Insere um documento coletado na tabela `documentos`. Silenciosamente
    pulado (com aviso) se as credenciais não estiverem configuradas.

    TODO (requer decisão de produto, não implementado aqui): este insert é
    sempre um append simples — a tabela `documentos` não tem constraint
    única além do `id` (uuid, gerado automaticamente), então reexecutar o
    coletor no mesmo dia (ex.: reprocessar fontes que deram erro, ou um
    futuro cron disparando em duplicidade) insere linhas duplicadas para a
    mesma fonte/documento em vez de atualizar a existente. Duas opções,
    a confirmar com o time antes de mexer no schema em produção:
      1) Manter como log append-only (uma linha por execução, mesmo que no
         mesmo dia) — comportamento atual já é isso; só falta documentar a
         decisão explicitamente (README/CLAUDE.md) para quem consumir a
         tabela em web/relatorios saber que pode haver múltiplas linhas por
         fonte/dia.
      2) Trocar para "um snapshot por fonte por dia/documento": exigiria
         adicionar um índice único na tabela (ex.: em (fonte, url,
         date_trunc('day', data_coleta)) ou (fonte, url, data_publicacao))
         e trocar `.insert()` por `.upsert(..., on_conflict=...)`.
    """
    client = _client()
    if client is None:
        return

    linha = {
        "grupo": documento["grupo"],
        "fonte": documento["fonte"],
        "url": documento["url"],
        "titulo": documento.get("titulo"),
        "texto": documento.get("texto"),
        "data_coleta": documento.get("data_coleta"),
        "data_publicacao": documento.get("data_publicacao"),
        "status": documento["status"],
        "detalhe": documento.get("detalhe"),
        "embedding": gerar_embedding(documento.get("texto") or ""),
    }
    try:
        client.table("documentos").insert(linha).execute()
    except Exception as exc:
        print(f"[supabase_sink] falha ao gravar '{documento['fonte']}' no Supabase: {exc}")
