# -*- coding: utf-8 -*-
"""Gera embeddings para documentos já gravados no Supabase que ainda não têm
(ex.: coletados antes da coluna `embedding` existir).

Uso:
    python -m collector.backfill_embeddings
"""

import os
import sys
import time

from dotenv import load_dotenv

from .embeddings import gerar_embedding

load_dotenv()

DELAY_ENTRE_CHAMADAS = 15.0  # segundos — conta nova na Voyage parece ter rate limit bem baixo


def main() -> int:
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:
        print("SUPABASE_URL/SUPABASE_SERVICE_ROLE_KEY não configuradas em .env — nada a fazer.")
        return 1

    from supabase import create_client
    client = create_client(url, key)

    resultado = (
        client.table("documentos")
        .select("id, fonte, texto")
        .is_("embedding", "null")
        .execute()
    )
    pendentes = resultado.data or []
    print(f"{len(pendentes)} documento(s) sem embedding.")

    ok = erro = pulados = 0
    for doc in pendentes:
        texto = doc.get("texto") or ""
        if not texto.strip():
            print(f"  - {doc['fonte']}: sem texto, pulando.")
            pulados += 1
            continue

        embedding = gerar_embedding(texto)
        time.sleep(DELAY_ENTRE_CHAMADAS)
        if embedding is None:
            print(f"  - {doc['fonte']}: falha ao gerar embedding.")
            erro += 1
            continue

        try:
            client.table("documentos").update({"embedding": embedding}).eq("id", doc["id"]).execute()
            print(f"  - {doc['fonte']}: embedding gravado.")
            ok += 1
        except Exception as exc:
            print(f"  - {doc['fonte']}: falha ao gravar embedding: {exc}")
            erro += 1

    print(f"\nResumo: {ok} atualizados, {erro} com erro, {pulados} pulados (sem texto).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
