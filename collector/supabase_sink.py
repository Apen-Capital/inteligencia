# -*- coding: utf-8 -*-
"""Grava os documentos coletados na tabela `documentos` do Supabase.

Lê as credenciais de variáveis de ambiente (arquivo .env, nunca commitado).
Se SUPABASE_URL/SUPABASE_SERVICE_ROLE_KEY não estiverem configuradas, a
gravação é pulada com um aviso — a coleta local (JSON) continua funcionando
normalmente, sem depender do Supabase.
"""

import os

from dotenv import load_dotenv

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
    pulado (com aviso) se as credenciais não estiverem configuradas."""
    client = _client()
    if client is None:
        return

    linha = {
        "grupo": documento["grupo"],
        "fonte": documento["fonte"],
        "url": documento["url"],
        "titulo": documento.get("titulo"),
        "texto": documento.get("texto"),
        "data_publicacao": documento.get("data_publicacao"),
        "status": documento["status"],
        "detalhe": documento.get("detalhe"),
    }
    try:
        client.table("documentos").insert(linha).execute()
    except Exception as exc:
        print(f"[supabase_sink] falha ao gravar '{documento['fonte']}' no Supabase: {exc}")
