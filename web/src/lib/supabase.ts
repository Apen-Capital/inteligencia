import { createClient } from "@supabase/supabase-js";

export type Documento = {
  id: string;
  grupo: string;
  fonte: string;
  url: string;
  titulo: string | null;
  texto: string | null;
  data_coleta: string;
  data_publicacao: string | null;
  status: "ok" | "parcial" | "erro";
  detalhe: string | null;
};

export function getSupabaseClient() {
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const anonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

  if (!url || !anonKey) {
    throw new Error(
      "NEXT_PUBLIC_SUPABASE_URL / NEXT_PUBLIC_SUPABASE_ANON_KEY não configuradas (ver web/.env.local.example)."
    );
  }

  return createClient(url, anonKey);
}
