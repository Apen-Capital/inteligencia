# -*- coding: utf-8 -*-
"""Coleta de artigos de sites de notícia (grupo "Site de noticias").

Baixa o HTML e usa trafilatura para extrair título, texto principal e data
de publicação. Sites com paywall (ex.: FT, WSJ) tendem a retornar pouco ou
nenhum texto útil — isso é tratado como status "parcial", não como erro.
"""

import trafilatura

from ..common import MIN_TEXTO_OK, baixar_pagina, montar_documento
from ..sources import Fonte


def fetch_article(fonte: Fonte) -> dict:
    resp, erro = baixar_pagina(fonte)
    if erro:
        return erro

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
