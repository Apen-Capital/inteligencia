import { Badge } from "@/components/ui/badge";
import { getSupabaseClient, type Documento } from "@/lib/supabase";

export const dynamic = "force-dynamic";

const STATUS_ESTILO: Record<Documento["status"], string> = {
  ok: "border-status-ok/40 text-status-ok bg-status-ok/10",
  parcial: "border-status-parcial/40 text-status-parcial bg-status-parcial/10",
  erro: "border-status-erro/40 text-status-erro bg-status-erro/10",
};

export default async function RelatoriosPage() {
  let documentos: Documento[] = [];
  let erroCarregamento: string | null = null;

  try {
    const supabase = getSupabaseClient();
    const { data, error } = await supabase
      .from("documentos")
      .select("*")
      .order("data_coleta", { ascending: false })
      .limit(200);

    if (error) throw error;
    documentos = data ?? [];
  } catch (err) {
    erroCarregamento = err instanceof Error ? err.message : String(err);
  }

  const contagem = documentos.reduce(
    (acc, d) => ({ ...acc, [d.status]: (acc[d.status] ?? 0) + 1 }),
    {} as Record<string, number>
  );

  return (
    <div className="space-y-8">
      <div className="space-y-2">
        <p className="font-mono text-xs uppercase tracking-widest text-muted-foreground">
          Gestão de Relatórios
        </p>
        <h1 className="font-display text-3xl text-foreground">
          Documentos coletados
        </h1>
        <p className="max-w-2xl text-sm text-muted-foreground">
          Fontes abertas rastreadas automaticamente pelo coletor (ver{" "}
          <code className="font-mono text-xs text-foreground/80">
            collector/sources.py
          </code>
          ). A estrutura final dos relatórios (Diário / Cliente / Interno)
          ainda não foi recebida — esta é a matéria-prima bruta.
        </p>
        {documentos.length > 0 && (
          <div className="flex gap-4 pt-2 font-mono text-xs">
            <span className="text-status-ok">{contagem.ok ?? 0} ok</span>
            <span className="text-status-parcial">
              {contagem.parcial ?? 0} parcial
            </span>
            <span className="text-status-erro">{contagem.erro ?? 0} erro</span>
          </div>
        )}
      </div>

      {erroCarregamento && (
        <div className="border border-status-erro/40 bg-status-erro/5 px-5 py-4">
          <p className="font-mono text-xs uppercase tracking-widest text-status-erro">
            Falha ao carregar
          </p>
          <p className="mt-1 text-sm text-muted-foreground">
            {erroCarregamento}
          </p>
        </div>
      )}

      {!erroCarregamento && documentos.length === 0 && (
        <div className="border border-dashed border-border px-5 py-10 text-center">
          <p className="text-sm text-muted-foreground">
            Nenhum documento coletado ainda. Rode{" "}
            <code className="font-mono text-xs text-foreground/80">
              python -m collector.run
            </code>{" "}
            (com{" "}
            <code className="font-mono text-xs text-foreground/80">
              SUPABASE_SERVICE_ROLE_KEY
            </code>{" "}
            configurada em <code className="font-mono text-xs">.env</code>).
          </p>
        </div>
      )}

      {documentos.length > 0 && (
        <div className="divide-y divide-border border-y border-border">
          {documentos.map((doc) => (
            <details key={doc.id} className="group px-1 py-3">
              <summary className="flex cursor-pointer list-none items-center gap-4 [&::-webkit-details-marker]:hidden">
                <span className="w-36 shrink-0 font-mono text-[11px] text-muted-foreground">
                  {new Date(doc.data_coleta).toLocaleString("pt-BR", {
                    day: "2-digit",
                    month: "2-digit",
                    hour: "2-digit",
                    minute: "2-digit",
                  })}
                </span>
                <Badge
                  variant="outline"
                  className={`${STATUS_ESTILO[doc.status]} shrink-0 font-mono`}
                >
                  {doc.status}
                </Badge>
                <span className="w-40 shrink-0 truncate font-mono text-xs text-muted-foreground">
                  {doc.grupo}
                </span>
                <span className="truncate font-display text-base text-foreground group-open:whitespace-normal">
                  {doc.fonte}
                  {doc.titulo && (
                    <span className="ml-2 font-sans text-sm text-muted-foreground">
                      — {doc.titulo}
                    </span>
                  )}
                </span>
              </summary>
              <p className="mt-3 ml-40 max-w-3xl whitespace-pre-wrap text-sm leading-relaxed text-muted-foreground">
                {doc.texto || doc.detalhe || "(sem conteúdo)"}
              </p>
            </details>
          ))}
        </div>
      )}
    </div>
  );
}
