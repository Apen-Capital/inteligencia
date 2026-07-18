# -*- coding: utf-8 -*-
"""
collector/sources.py

Representação em Python da planilha "Bases de dados para relatório.xlsx".

Contém as fontes de informação utilizadas na elaboração de relatórios,
organizadas por grupo (site de notícias, portal de plataforma, dados de
mercado e canais do YouTube), com nome da fonte, link de acesso, se
exige login e observações relevantes.

Uso:
    from collector.sources import FONTES, listar_por_grupo, buscar_por_fonte, fontes_mvp

    print(listar_por_grupo("Dados de mercado"))
    print(buscar_por_fonte("InfoMoney"))
    print(fontes_mvp())  # só as fontes abertas (sem login) do protótipo atual
"""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Fonte:
    """Representa uma linha da planilha: uma fonte de informação."""
    grupo: str
    fonte: str
    link: str
    obs: Optional[str] = None
    requer_login: bool = False


# ---------------------------------------------------------------------------
# Base de dados (equivalente às linhas da planilha)
# ---------------------------------------------------------------------------
FONTES: list[Fonte] = [
    # Site de notícias
    Fonte("Site de noticias", "The economist", "https://www.economist.com/"),
    Fonte("Site de noticias", "Financial time", "https://www.ft.com/"),
    Fonte("Site de noticias", "Wall Street Journal", "https://www.wsj.com/"),
    Fonte("Site de noticias", "Brazil journal", "https://braziljournal.com/"),
    Fonte("Site de noticias", "CNN brasil", "https://www.cnnbrasil.com.br/"),
    Fonte("Site de noticias", "Valor Economico", "https://valor.globo.com/"),
    Fonte("Site de noticias", "BBC business", "https://www.bbc.com/business"),
    Fonte("Site de noticias", "NeoFeed negócios", "https://neofeed.com.br/"),
    Fonte("Site de noticias", "Reuters breaking", "https://www.reuters.com/"),
    Fonte("Site de noticias", "Times brasil", "https://timesbrasil.com.br/"),
    Fonte("Site de noticias", "Bloomberg Línea", "https://www.bloomberglinea.com.br/"),
    Fonte("Site de noticias", "InfoMoney", "https://www.infomoney.com.br/"),

    # Portal de plataforma (exigem login — não implementado neste protótipo)
    Fonte("Portal de plataforma", "XP", "https://conteudos.xpi.com.br/", "Precisa de login", requer_login=True),
    Fonte("Portal de plataforma", "BTG", "https://content.btgpactual.com/", "Precisa de login", requer_login=True),
    Fonte("Portal de plataforma", "Nord Research", "https://members.nordinvestimentos.com.br/", "Precisa de login", requer_login=True),

    # Dados de mercado
    Fonte("Dados de mercado", "Street Stats", "https://streetstats.finance/", "Dados do mercado de renda fixa americana"),
    Fonte("Dados de mercado", "Brazil stock", "https://worldperatio.com/area/brazil/", "P/L da bolsa"),
    Fonte("Dados de mercado", "FedWatch", "https://www.cmegroup.com/markets/interest-rates/cme-fedwatch-tool.html", "Monitoramento de movimento do FED"),

    # Canais de Youtube
    Fonte("Canais de Youtube", "WHG", "https://www.youtube.com/@wealthhighgovernance", "Comitê mensal de alocação da XP"),
    Fonte("Canais de Youtube", "XP", "https://www.youtube.com/playlist?list=PLMl5SicO7iPApIjt38YmLJ_RolCHx3TqS", "Comitê macro mensal da WHG"),
    Fonte("Canais de Youtube", "Encore", "https://www.youtube.com/@EncoreAssetManagement", "Comitê macro mensal da Encore"),
]


# ---------------------------------------------------------------------------
# Funções utilitárias
# ---------------------------------------------------------------------------
def listar_grupos() -> list[str]:
    """Retorna a lista de grupos únicos, na ordem em que aparecem."""
    vistos: dict[str, None] = {}
    for f in FONTES:
        vistos.setdefault(f.grupo, None)
    return list(vistos.keys())


def listar_por_grupo(grupo: str) -> list[Fonte]:
    """Retorna todas as fontes pertencentes a um grupo (case-insensitive)."""
    grupo_lower = grupo.strip().lower()
    return [f for f in FONTES if f.grupo.lower() == grupo_lower]


def buscar_por_fonte(nome: str) -> Optional[Fonte]:
    """Busca uma fonte pelo nome (case-insensitive, correspondência exata)."""
    nome_lower = nome.strip().lower()
    for f in FONTES:
        if f.fonte.lower() == nome_lower:
            return f
    return None


def buscar(texto: str) -> list[Fonte]:
    """Busca fontes cujo nome, grupo ou observação contenha o texto informado."""
    texto_lower = texto.strip().lower()
    resultado = []
    for f in FONTES:
        campos = [f.grupo, f.fonte, f.obs or ""]
        if any(texto_lower in campo.lower() for campo in campos):
            resultado.append(f)
    return resultado


def para_dicionarios() -> list[dict]:
    """Converte a lista de fontes em uma lista de dicionários (útil para JSON/CSV)."""
    return [
        {"Grupo": f.grupo, "Fonte": f.fonte, "Link": f.link, "Obs": f.obs, "RequerLogin": f.requer_login}
        for f in FONTES
    ]


def fontes_mvp() -> list[Fonte]:
    """Retorna só as fontes sem exigência de login — escopo do protótipo atual de coleta."""
    return [f for f in FONTES if not f.requer_login]


# ---------------------------------------------------------------------------
# Execução direta: mostra um resumo da base
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print(f"Total de fontes cadastradas: {len(FONTES)}\n")
    for grupo in listar_grupos():
        fontes_grupo = listar_por_grupo(grupo)
        print(f"## {grupo} ({len(fontes_grupo)})")
        for f in fontes_grupo:
            obs_str = f" — {f.obs}" if f.obs else ""
            print(f"  - {f.fonte}: {f.link}{obs_str}")
        print()
