import { NextResponse } from "next/server";
import { getSupabaseClient } from "@/lib/supabase";
import { embedarConsulta } from "@/lib/voyage";

// Busca semântica real via Voyage AI (embeddings) + pgvector (Supabase).
// Geração de resposta em linguagem natural (Claude) ainda não está
// configurada (falta ANTHROPIC_API_KEY) — por enquanto retornamos os
// documentos mais relevantes encontrados, sem fingir uma resposta gerada.
export async function POST(request: Request) {
  let corpo: unknown;
  try {
    corpo = await request.json();
  } catch {
    return NextResponse.json(
      { erro: "Corpo da requisição inválido, esperado JSON." },
      { status: 400 }
    );
  }

  if (!corpo || typeof corpo !== "object") {
    return NextResponse.json(
      { erro: "Corpo da requisição inválido, esperado JSON." },
      { status: 400 }
    );
  }

  const { mensagem } = corpo as { mensagem?: unknown };

  if (!mensagem || typeof mensagem !== "string") {
    return NextResponse.json(
      { erro: "Campo 'mensagem' é obrigatório." },
      { status: 400 }
    );
  }

  if (!process.env.VOYAGE_API_KEY) {
    return NextResponse.json({
      resposta:
        "Integração com a Voyage AI ainda não configurada. Configure VOYAGE_API_KEY para habilitar busca semântica sobre os documentos coletados (ver README.md).",
      resultados: [],
    });
  }

  const embedding = await embedarConsulta(mensagem);
  if (!embedding) {
    return NextResponse.json(
      { erro: "Não foi possível gerar o embedding da pergunta. Tente novamente." },
      { status: 502 }
    );
  }

  const supabase = getSupabaseClient();
  const { data, error } = await supabase.rpc("match_documentos", {
    query_embedding: embedding,
    match_count: 5,
  });

  if (error) {
    return NextResponse.json(
      { erro: `Falha ao buscar documentos: ${error.message}` },
      { status: 502 }
    );
  }

  const resultados = (data ?? []) as Array<{
    fonte: string;
    grupo: string;
    titulo: string | null;
    texto: string | null;
    url: string;
    similaridade: number;
  }>;

  return NextResponse.json({
    resposta: resultados.length
      ? `Encontrei ${resultados.length} documento(s) relacionado(s) a "${mensagem}" (busca semântica via Voyage AI). Geração de resposta em linguagem natural ainda não configurada (falta ANTHROPIC_API_KEY) — veja os trechos recuperados abaixo.`
      : "Nenhum documento com embedding calculado corresponde a essa pergunta ainda. Rode o backfill (collector/backfill_embeddings.py) ou colete mais dados.",
    resultados: resultados.map((r) => ({
      fonte: r.fonte,
      grupo: r.grupo,
      titulo: r.titulo,
      trecho: (r.texto ?? "").slice(0, 400),
      url: r.url,
      similaridade: Math.round(r.similaridade * 100) / 100,
    })),
  });
}
