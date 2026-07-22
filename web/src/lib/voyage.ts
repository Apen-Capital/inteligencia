// Chamada direta à API REST da Voyage (sem SDK — só fetch nativo).
// Docs: https://docs.voyageai.com/docs/api-key-and-installation
const MODELO = "voyage-finance-2";
const URL = "https://api.voyageai.com/v1/embeddings";

export async function embedarConsulta(texto: string): Promise<number[] | null> {
  const chave = process.env.VOYAGE_API_KEY;
  if (!chave || !texto.trim()) return null;

  try {
    const resp = await fetch(URL, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${chave}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        model: MODELO,
        input: [texto],
        input_type: "query",
      }),
    });

    if (!resp.ok) {
      console.error("[voyage] falha ao gerar embedding da consulta:", resp.status, await resp.text());
      return null;
    }

    const dados = await resp.json();
    return dados.data?.[0]?.embedding ?? null;
  } catch (err) {
    console.error("[voyage] erro ao chamar a API:", err);
    return null;
  }
}
