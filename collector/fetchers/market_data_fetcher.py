# -*- coding: utf-8 -*-
"""Coleta de páginas de dados de mercado (grupo "Dados de mercado").

Estas páginas (StreetStats, worldperatio, CME FedWatch) não são artigos —
são paineis/dashboards com layout próprio. Nesta primeira etapa apenas
guardamos um snapshot de texto da página; extrair o número específico de
cada uma (ex.: valor do P/L, probabilidade do FedWatch) fica para uma
iteração futura, com um parser dedicado por fonte.
"""

import httpx
import trafilatura

from ..common import HEADERS, montar_documento
from ..sources import Fonte

TIMEOUT = 20.0


def fetch_market_page(fonte: Fonte) -> dict:
    try:
        resp = httpx.get(fonte.link, headers=HEADERS, timeout=TIMEOUT, follow_redirects=True)
        resp.raise_for_status()
    except Exception as exc:
        return montar_documento(
            grupo=fonte.grupo, fonte=fonte.fonte, url=fonte.link,
            status="erro", detalhe=f"falha ao baixar a página: {exc}",
        )

    texto = trafilatura.extract(resp.text, include_comments=False, favor_recall=True) or ""

    if not texto.strip():
        return montar_documento(
            grupo=fonte.grupo, fonte=fonte.fonte, url=fonte.link,
            status="parcial", detalhe="não foi possível extrair texto (página provavelmente renderiza dados via JavaScript)",
        )

    return montar_documento(
        grupo=fonte.grupo, fonte=fonte.fonte, url=fonte.link,
        titulo=fonte.fonte, texto=texto,
        status="ok", detalhe="snapshot bruto da página — parsing específico do dado ainda não implementado",
    )
