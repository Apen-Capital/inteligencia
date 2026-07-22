# -*- coding: utf-8 -*-
"""Coleta de uploads recentes de canais/playlists do YouTube (grupo "Canais de Youtube").

Não usa a API oficial do YouTube (sem necessidade de chave/API key): resolve
o channel_id a partir da página do canal e lê o feed RSS público do YouTube,
que lista os uploads mais recentes com título, link e data.
"""

import re
from urllib.parse import parse_qs, urlparse

import feedparser

from ..common import baixar_pagina, montar_documento
from ..sources import Fonte

# Ordem importa: tenta o link canônico primeiro (mais estável), depois "externalId"
# (o campo "channelId" do JSON embutido não é mais confiável na página atual do YouTube).
CHANNEL_ID_PATTERNS = [
    re.compile(r'canonical" href="https://www\.youtube\.com/channel/(UC[0-9A-Za-z_-]{22})"'),
    re.compile(r'"externalId":"(UC[0-9A-Za-z_-]{22})"'),
    re.compile(r'/channel/(UC[0-9A-Za-z_-]{22})'),
]


def _extrair_channel_id(html: str) -> str | None:
    for pattern in CHANNEL_ID_PATTERNS:
        match = pattern.search(html)
        if match:
            return match.group(1)
    return None


def _resolver_feed_url(fonte: Fonte) -> tuple[str, str] | None:
    """Retorna (tipo, id) — tipo é 'channel_id' ou 'playlist_id' — ou None se não resolver."""
    parsed = urlparse(fonte.link)
    qs = parse_qs(parsed.query)

    if "list" in qs:
        return "playlist_id", qs["list"][0]

    if "/channel/" in parsed.path:
        channel_id = parsed.path.split("/channel/")[-1].split("/")[0]
        return "channel_id", channel_id

    # Handle (@nome) ou /c/ ou /user/: precisa buscar o channelId na página.
    # Em caso de erro de rede, devolvemos None (quem chama, fetch_youtube, já
    # gera seu próprio documento de erro genérico nesse caso).
    resp, erro = baixar_pagina(fonte)
    if erro:
        return None

    channel_id = _extrair_channel_id(resp.text)
    if channel_id:
        return "channel_id", channel_id
    return None


def fetch_youtube(fonte: Fonte) -> dict:
    resolvido = _resolver_feed_url(fonte)
    if resolvido is None:
        return montar_documento(
            grupo=fonte.grupo, fonte=fonte.fonte, url=fonte.link,
            status="erro", detalhe="não foi possível resolver channel_id/playlist_id a partir da URL",
        )

    tipo, valor = resolvido
    feed_url = f"https://www.youtube.com/feeds/videos.xml?{tipo}={valor}"

    resp, erro = baixar_pagina(fonte, url=feed_url)
    if erro:
        return erro

    feed = feedparser.parse(resp.content)
    entradas = feed.entries[:15]

    if not entradas:
        return montar_documento(
            grupo=fonte.grupo, fonte=fonte.fonte, url=fonte.link,
            status="parcial", detalhe="feed encontrado mas sem vídeos listados",
        )

    linhas = [
        f"- {e.get('title', '(sem título)')} ({e.get('published', '?')}): {e.get('link', '')}"
        for e in entradas
    ]

    return montar_documento(
        grupo=fonte.grupo, fonte=fonte.fonte, url=fonte.link,
        titulo=f"Uploads recentes — {fonte.fonte}",
        texto="\n".join(linhas),
        status="ok", detalhe=f"{len(entradas)} vídeos listados via feed RSS",
    )
