# -*- coding: utf-8 -*-
"""Utilitários compartilhados pelos fetchers: cabeçalhos HTTP, slug de arquivo,
o download padrão (GET + tratamento de erro) e o formato padrão de documento
salvo em data/raw/."""

import re
import unicodedata
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional

import httpx

if TYPE_CHECKING:
    from .sources import Fonte

USER_AGENT = "ApenIntelCollector/0.1 (+contato: operacional@apencapital.com.br)"

HEADERS = {"User-Agent": USER_AGENT}

# timeout padrão (segundos) para o download das páginas/feeds das fontes
TIMEOUT_PADRAO = 20.0

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


def baixar_pagina(
    fonte: "Fonte", url: Optional[str] = None, timeout: float = TIMEOUT_PADRAO
) -> tuple[Optional[httpx.Response], Optional[dict]]:
    """GET padrão (HEADERS + raise_for_status) usado por todos os fetchers.

    Retorna (resp, None) em caso de sucesso, ou (None, documento_de_erro) se o
    download falhar — já no formato pronto para o fetcher retornar direto:

        resp, erro = baixar_pagina(fonte)
        if erro:
            return erro

    `url` permite baixar uma URL diferente de `fonte.link` (ex.: um feed RSS
    resolvido a partir da página do canal) mantendo `fonte`/`fonte.link` no
    documento de erro, que sempre referencia a fonte original.
    """
    try:
        resp = httpx.get(url or fonte.link, headers=HEADERS, timeout=timeout, follow_redirects=True)
        resp.raise_for_status()
        return resp, None
    except Exception as exc:
        return None, montar_documento(
            grupo=fonte.grupo, fonte=fonte.fonte, url=fonte.link,
            status="erro", detalhe=f"falha ao baixar a página: {exc}",
        )
