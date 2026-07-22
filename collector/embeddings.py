# -*- coding: utf-8 -*-
"""Gera embeddings via Voyage AI (modelo `voyage-finance-2`, 1024 dimensões).

Usa a API REST diretamente (sem SDK extra — só `httpx`, já é dependência do
projeto). Docs: https://docs.voyageai.com/docs/api-key-and-installation
"""

import os

import httpx

MODELO = "voyage-finance-2"
URL = "https://api.voyageai.com/v1/embeddings"
TIMEOUT = 30.0

# Voyage aceita até ~32K tokens por texto neste modelo; um corte defensivo em
# caracteres evita mandar um texto absurdamente grande por engano.
MAX_CHARS = 20_000


def gerar_embedding(texto: str, input_type: str = "document") -> list[float] | None:
    """Retorna o vetor de embedding do texto, ou None se VOYAGE_API_KEY não
    estiver configurada, o texto estiver vazio, ou a chamada falhar."""
    chave = os.environ.get("VOYAGE_API_KEY")
    if not chave or not texto or not texto.strip():
        return None

    try:
        resp = httpx.post(
            URL,
            headers={"Authorization": f"Bearer {chave}"},
            json={
                "model": MODELO,
                "input": [texto[:MAX_CHARS]],
                "input_type": input_type,
            },
            timeout=TIMEOUT,
        )
        resp.raise_for_status()
        return resp.json()["data"][0]["embedding"]
    except Exception as exc:
        print(f"[embeddings] falha ao gerar embedding via Voyage: {exc}")
        return None
