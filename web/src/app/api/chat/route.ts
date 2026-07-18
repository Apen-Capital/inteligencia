import { NextResponse } from "next/server";

// Stub: ainda não há integração real (busca semântica via Voyage AI +
// geração via Claude). Ver README.md, seção "Decisões — Supabase e Front",
// para o passo a passo de como habilitar isso quando a VOYAGE_API_KEY existir.
export async function POST(request: Request) {
  const { mensagem } = await request.json();

  if (!mensagem || typeof mensagem !== "string") {
    return NextResponse.json(
      { erro: "Campo 'mensagem' é obrigatório." },
      { status: 400 }
    );
  }

  const temChaveVoyage = Boolean(process.env.VOYAGE_API_KEY);

  return NextResponse.json({
    resposta: temChaveVoyage
      ? "VOYAGE_API_KEY detectada, mas a busca semântica ainda não foi implementada neste stub."
      : "Integração com a Voyage AI ainda não configurada. Configure VOYAGE_API_KEY para habilitar busca semântica sobre os documentos coletados (ver README.md).",
  });
}
