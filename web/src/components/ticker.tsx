import { getSupabaseClient } from "@/lib/supabase";

async function buscarManchetes() {
  try {
    const supabase = getSupabaseClient();
    const { data } = await supabase
      .from("documentos")
      .select("fonte, titulo")
      .not("titulo", "is", null)
      .order("data_coleta", { ascending: false })
      .limit(12);
    return data ?? [];
  } catch {
    return [];
  }
}

export async function Ticker() {
  const manchetes = await buscarManchetes();

  if (manchetes.length === 0) {
    return (
      <div className="border-b border-border bg-card/60 py-2">
        <p className="mx-auto max-w-6xl px-6 font-mono text-xs text-muted-foreground">
          Aguardando a primeira coleta para popular o ticker de manchetes...
        </p>
      </div>
    );
  }

  const itens = [...manchetes, ...manchetes];

  return (
    <div className="overflow-hidden border-b border-border bg-card/60 py-2">
      <div className="ticker-track flex w-max gap-10 whitespace-nowrap">
        {itens.map((doc, i) => (
          <span key={i} className="font-mono text-xs text-primary">
            <span className="text-muted-foreground">{doc.fonte}</span>
            {" — "}
            {doc.titulo}
          </span>
        ))}
      </div>
    </div>
  );
}
