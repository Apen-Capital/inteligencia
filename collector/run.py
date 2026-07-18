# -*- coding: utf-8 -*-
"""Orquestrador do protótipo de coleta (fontes abertas).

Uso:
    python -m collector.run

Lê collector/sources.py (fontes_mvp — só fontes sem login), despacha cada
fonte para o fetcher correspondente ao seu grupo, salva o documento
resultante em data/raw/<AAAA-MM-DD>/<fonte>.json e imprime um resumo.

As 3 fontes que exigem login (XP, BTG, Nord Research) são listadas mas
puladas nesta etapa — ver README.md, seção "Próximos passos".
"""

import json
import sys
import time
from datetime import date
from pathlib import Path

from .common import slugify
from .fetchers.article_fetcher import fetch_article
from .fetchers.market_data_fetcher import fetch_market_page
from .fetchers.youtube_fetcher import fetch_youtube
from .sources import FONTES, fontes_mvp
from .supabase_sink import salvar_documento

DELAY_ENTRE_REQUISICOES = 2.0  # segundos — etiqueta básica de scraping

FETCHER_POR_GRUPO = {
    "Site de noticias": fetch_article,
    "Dados de mercado": fetch_market_page,
    "Canais de Youtube": fetch_youtube,
}


def main() -> int:
    saida_dir = Path("data") / "raw" / date.today().isoformat()
    saida_dir.mkdir(parents=True, exist_ok=True)

    fontes_login = [f for f in FONTES if f.requer_login]
    if fontes_login:
        print(f"Pulando {len(fontes_login)} fonte(s) que exigem login (fora do escopo deste protótipo):")
        for f in fontes_login:
            print(f"  - {f.fonte}")
        print()

    resultados: dict[str, list[str]] = {"ok": [], "parcial": [], "erro": []}

    fontes = fontes_mvp()
    for i, fonte in enumerate(fontes):
        fetcher = FETCHER_POR_GRUPO.get(fonte.grupo)
        if fetcher is None:
            print(f"[AVISO] Sem fetcher para o grupo '{fonte.grupo}' (fonte: {fonte.fonte}) — pulando.")
            continue

        print(f"Coletando: {fonte.fonte} ({fonte.grupo})...")
        try:
            documento = fetcher(fonte)
        except Exception as exc:  # nunca deixa uma fonte derrubar o pipeline inteiro
            documento = {
                "grupo": fonte.grupo, "fonte": fonte.fonte, "url": fonte.link,
                "status": "erro", "detalhe": f"exceção não tratada: {exc}",
            }

        status = documento.get("status", "erro")
        resultados.setdefault(status, []).append(fonte.fonte)

        arquivo_saida = saida_dir / f"{slugify(fonte.fonte)}.json"
        arquivo_saida.write_text(json.dumps(documento, ensure_ascii=False, indent=2), encoding="utf-8")
        salvar_documento(documento)

        if i < len(fontes) - 1:
            time.sleep(DELAY_ENTRE_REQUISICOES)

    print("\n--- Resumo ---")
    for status in ("ok", "parcial", "erro"):
        nomes = resultados.get(status, [])
        print(f"{status}: {len(nomes)}" + (f" ({', '.join(nomes)})" if nomes else ""))
    print(f"\nDocumentos salvos em: {saida_dir}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
