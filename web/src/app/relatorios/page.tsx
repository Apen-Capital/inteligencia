import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { getSupabaseClient, type Documento } from "@/lib/supabase";

export const dynamic = "force-dynamic";

const STATUS_VARIANTE: Record<Documento["status"], "default" | "secondary" | "destructive"> = {
  ok: "default",
  parcial: "secondary",
  erro: "destructive",
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

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-zinc-900 dark:text-zinc-50">
          Gestão de Relatórios
        </h1>
        <p className="text-sm text-zinc-500">
          Documentos brutos coletados automaticamente das fontes abertas (ver{" "}
          <code>collector/sources.py</code>). A estrutura final dos 3 tipos de
          relatório (Diário/Cliente/Interno) ainda não foi recebida — esta
          tabela mostra o que já conseguimos coletar hoje.
        </p>
      </div>

      {erroCarregamento && (
        <Card className="border-destructive">
          <CardHeader>
            <CardTitle className="text-destructive text-sm">
              Não foi possível carregar os documentos
            </CardTitle>
          </CardHeader>
          <CardContent className="text-sm text-zinc-600 dark:text-zinc-400">
            {erroCarregamento}
          </CardContent>
        </Card>
      )}

      {!erroCarregamento && documentos.length === 0 && (
        <Card>
          <CardContent className="py-8 text-center text-sm text-zinc-500">
            Nenhum documento coletado ainda. Rode{" "}
            <code>python -m collector.run</code> (com{" "}
            <code>SUPABASE_SERVICE_ROLE_KEY</code> configurada em{" "}
            <code>.env</code>) para popular esta tabela.
          </CardContent>
        </Card>
      )}

      {documentos.length > 0 && (
        <Card>
          <CardContent className="p-0">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Fonte</TableHead>
                  <TableHead>Grupo</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Coletado em</TableHead>
                  <TableHead>Conteúdo</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {documentos.map((doc) => (
                  <TableRow key={doc.id}>
                    <TableCell className="font-medium">{doc.fonte}</TableCell>
                    <TableCell className="text-zinc-500">{doc.grupo}</TableCell>
                    <TableCell>
                      <Badge variant={STATUS_VARIANTE[doc.status]}>
                        {doc.status}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-zinc-500 whitespace-nowrap">
                      {new Date(doc.data_coleta).toLocaleString("pt-BR")}
                    </TableCell>
                    <TableCell className="max-w-md">
                      <details>
                        <summary className="cursor-pointer text-zinc-600 dark:text-zinc-400">
                          {doc.titulo || doc.detalhe || "(sem título)"}
                        </summary>
                        <p className="mt-2 whitespace-pre-wrap text-xs text-zinc-500">
                          {doc.texto || doc.detalhe || "(sem conteúdo)"}
                        </p>
                      </details>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
