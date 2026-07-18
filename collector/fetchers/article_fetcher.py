# -*- coding: utf-8 -*-
"""Coleta de artigos de sites de notícia (grupo "Site de noticias").

Baixa o HTML e usa trafilatura para extrair título, texto principal e data
de publicação. Sites com paywall (ex.: FT, WSJ) tendem a retornar pouco ou
nenhum texto útil — isso é tratado como status "parcial", não como erro.
"""

import httpx
import trafilatura

from ..common import HEADERS, MIN_TEXTO_OK, montar_documento
from ..sources import Fonte

TIMEOUT = 20.0


def fetch_article(fonte: Fonte) -> dict:
    try:
        resp = httpx.get(fonte.link, headers=HEADERS, timeout=TIMEOUT, follow_redirects=True)
        resp.raise_for_status()
    except Exception as exc:
        return montar_documento(
            grupo=fonte.grupo, fonte=fonte.fonte, url=fonte.link,
            status="erro", detalhe=f"falha ao baixar a página: {exc}",
        )

    extraido = trafilatura.extract(
        resp.text, include_comments=False, with_metadata=True, output_format="json"
    )

    if not extraido:
        return montar_documento(
            grupo=fonte.grupo, fonte=fonte.fonte, url=fonte.link,
            status="parcial", detalhe="não foi possível extrair conteúdo (possível paywall/bloqueio)",
        )

    import json as _json
    dados = _json.loads(extraido)
    texto = dados.get("text") or ""
    titulo = dados.get("title") or fonte.fonte
    data_publicacao = dados.get("date")

    status = "ok" if len(texto) >= MIN_TEXTO_OK else "parcial"
    detalhe = "" if status == "ok" else "texto extraído muito curto (possível paywall/bloqueio)"

    return montar_documento(
        grupo=fonte.grupo, fonte=fonte.fonte, url=fonte.link,
        titulo=titulo, texto=texto, data_publicacao=data_publicacao,
        status=status, detalhe=detalhe,
    )
