# -*- coding: utf-8 -*-
"""Utilitários compartilhados pelos fetchers: cabeçalhos HTTP, slug de arquivo
e o formato padrão de documento salvo em data/raw/."""

import re
import unicodedata
from datetime import datetime, timezone
from typing import Optional

USER_AGENT = "ApenIntelCollector/0.1 (+contato: operacional@apencapital.com.br)"

HEADERS = {"User-Agent": USER_AGENT}

# tamanho mínimo de texto extraído para considerar a coleta "ok" em vez de
# "parcial" (heurística simples para detectar paywall/bloqueio)
MIN_TEXTO_OK = 500


def slugify(nome: str) -> str:
    nome_normalizado = unicodedata.normalize("NFKD", nome).encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", nome_normalizado).strip("-").lower()
    return slug or "fonte"


def montar_documento(
    *,
    grupo: str,
    fonte: str,
    url: str,
    titulo: str = "",
    texto: str = "",
    data_publicacao: Optional[str] = None,
    status: str = "ok",
    detalhe: str = "",
) -> dict:
    return {
        "grupo": grupo,
        "fonte": fonte,
        "url": url,
        "titulo": titulo,
        "texto": texto,
        "data_coleta": datetime.now(timezone.utc).isoformat(),
        "data_publicacao": data_publicacao,
        "status": status,
        "detalhe": detalhe,
    }
